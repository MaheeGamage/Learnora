"""
Service for managing and evolving user learning preferences.
"""
from typing import Dict, List, Optional, Any
from collections import Counter
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging

from .preferences import (
    UserLearningPreferences,
    ContentInteraction,
    InteractionTypeEnum,
    LearningStyleEnum
)
from app.features.content_discovery.models import UserProfile

logger = logging.getLogger(__name__)


class PreferenceService:
    """
    Manages user preferences and learns from interactions.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_preferences(self, user_id: int) -> UserLearningPreferences:
        """Get user preferences, creating default if not exists."""
        prefs = self.db.query(UserLearningPreferences).filter(
            UserLearningPreferences.user_id == user_id
        ).first()
        
        if not prefs:
            prefs = UserLearningPreferences(
                user_id=user_id,
                preferred_formats=[],
                learning_style=LearningStyleEnum.BALANCED,
                available_time_daily=60,
                knowledge_areas={},
                learning_goals=[],
                preferred_difficulty="intermediate",
                auto_evolve=True
            )
            self.db.add(prefs)
            self.db.commit()
            self.db.refresh(prefs)
        
        return prefs
    
    def update_preferences(
        self,
        user_id: int,
        preferred_formats: Optional[List[str]] = None,
        learning_style: Optional[str] = None,
        available_time_daily: Optional[int] = None,
        knowledge_areas: Optional[Dict[str, str]] = None,
        learning_goals: Optional[List[str]] = None,
        preferred_difficulty: Optional[str] = None,
        auto_evolve: Optional[bool] = None
    ) -> UserLearningPreferences:
        """Update user preferences explicitly."""
        prefs = self.get_or_create_preferences(user_id)
        
        if preferred_formats is not None:
            prefs.preferred_formats = preferred_formats
        if learning_style is not None:
            prefs.learning_style = LearningStyleEnum(learning_style)
        if available_time_daily is not None:
            prefs.available_time_daily = available_time_daily
        if knowledge_areas is not None:
            prefs.knowledge_areas = knowledge_areas
        if learning_goals is not None:
            prefs.learning_goals = learning_goals
        if preferred_difficulty is not None:
            prefs.preferred_difficulty = preferred_difficulty
        if auto_evolve is not None:
            prefs.auto_evolve = 1 if auto_evolve else 0
        
        prefs.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(prefs)
        
        return prefs
    
    def track_interaction(
        self,
        user_id: int,
        content_id: str,
        interaction_type: str,
        content_title: Optional[str] = None,
        content_type: Optional[str] = None,
        content_difficulty: Optional[str] = None,
        content_duration_minutes: Optional[int] = None,
        content_tags: Optional[List[str]] = None,
        duration_seconds: int = 0,
        rating: Optional[float] = None,
        completion_percentage: int = 0
    ) -> ContentInteraction:
        """Track a user interaction with content."""
        interaction = ContentInteraction(
            user_id=user_id,
            content_id=content_id,
            content_title=content_title,
            content_type=content_type,
            content_difficulty=content_difficulty,
            content_duration_minutes=content_duration_minutes,
            content_tags=content_tags or [],
            interaction_type=InteractionTypeEnum(interaction_type),
            duration_seconds=duration_seconds,
            rating=rating,
            completion_percentage=completion_percentage
        )
        
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        
        # Auto-evolve preferences if enabled
        prefs = self.get_or_create_preferences(user_id)
        if prefs.auto_evolve:
            self._evolve_preferences(user_id)
        
        # Sync with knowledge graph if content is significantly engaged with
        if completion_percentage >= 50 or interaction_type == InteractionTypeEnum.COMPLETED:
            try:
                self._sync_interaction_with_knowledge_graph(
                    user_id=user_id,
                    content_tags=content_tags or [],
                    content_difficulty=content_difficulty,
                    completion_percentage=completion_percentage,
                    interaction_type=interaction_type
                )
            except Exception as e:
                logger.error(f"Failed to sync interaction with knowledge graph: {e}")
                # Don't fail the interaction tracking if KG sync fails
        
        return interaction
    
    def _evolve_preferences(self, user_id: int) -> None:
        """
        Evolve user preferences based on interaction history.
        This is the AI that learns from user behavior!
        """
        prefs = self.get_or_create_preferences(user_id)
        
        # Get recent interactions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        interactions = self.db.query(ContentInteraction).filter(
            ContentInteraction.user_id == user_id,
            ContentInteraction.timestamp >= thirty_days_ago
        ).all()
        
        if not interactions:
            return
        
        # Learn preferred formats from what user actually engages with
        format_scores = Counter()
        difficulty_scores = Counter()
        total_duration = 0
        tag_scores = Counter()
        
        for interaction in interactions:
            # Weight interactions by type
            weight = self._interaction_weight(interaction.interaction_type)
            
            # Boost weight for completed/highly-rated content
            if interaction.completion_percentage >= 80:
                weight *= 1.5
            if interaction.rating and interaction.rating >= 4:
                weight *= 1.3
            
            # Track formats
            if interaction.content_type:
                format_scores[interaction.content_type.lower()] += weight
            
            # Track difficulty
            if interaction.content_difficulty:
                difficulty_scores[interaction.content_difficulty.lower()] += weight
            
            # Track duration
            if interaction.content_duration_minutes:
                total_duration += interaction.content_duration_minutes
            
            # Track tags/topics
            for tag in interaction.content_tags:
                tag_scores[tag.lower()] += weight
        
        # Update preferred formats (top 3)
        if format_scores:
            top_formats = [fmt for fmt, _ in format_scores.most_common(3)]
            prefs.preferred_formats = top_formats
        
        # Update preferred difficulty
        if difficulty_scores:
            top_difficulty = difficulty_scores.most_common(1)[0][0]
            prefs.preferred_difficulty = top_difficulty
        
        # Update available time (average duration of completed content)
        completed = [i for i in interactions if i.completion_percentage >= 80]
        if completed:
            avg_duration = sum(
                i.content_duration_minutes for i in completed if i.content_duration_minutes
            ) / len(completed)
            # Smooth update: 70% old value + 30% new value
            prefs.available_time_daily = int(
                0.7 * prefs.available_time_daily + 0.3 * avg_duration
            )
        
        # Update knowledge areas from top tags
        if tag_scores:
            knowledge_areas = {}
            for tag, score in tag_scores.most_common(10):
                # Infer proficiency level from interaction patterns
                tag_interactions = [
                    i for i in interactions
                    if tag in [t.lower() for t in i.content_tags]
                ]
                avg_difficulty = self._infer_proficiency(tag_interactions)
                knowledge_areas[tag] = avg_difficulty
            
            prefs.knowledge_areas = knowledge_areas
        
        # Infer learning style from content types and completion rates
        prefs.learning_style = self._infer_learning_style(interactions)
        
        prefs.updated_at = datetime.utcnow()
        self.db.commit()
    
    def _interaction_weight(self, interaction_type: InteractionTypeEnum) -> float:
        """Weight different interaction types."""
        weights = {
            InteractionTypeEnum.VIEWED: 1.0,
            InteractionTypeEnum.CLICKED: 1.2,
            InteractionTypeEnum.COMPLETED: 2.0,
            InteractionTypeEnum.BOOKMARKED: 1.5,
            InteractionTypeEnum.SHARED: 1.8,
            InteractionTypeEnum.RATED: 1.3,
        }
        return weights.get(interaction_type, 1.0)
    
    def _infer_proficiency(self, interactions: List[ContentInteraction]) -> str:
        """Infer proficiency level from interaction history."""
        if not interactions:
            return "beginner"
        
        # Look at difficulty of completed content
        completed = [i for i in interactions if i.completion_percentage >= 80]
        if not completed:
            return "beginner"
        
        difficulty_levels = {
            "beginner": 1,
            "intermediate": 2,
            "advanced": 3,
            "expert": 4
        }
        
        avg_level = sum(
            difficulty_levels.get(i.content_difficulty.lower(), 1)
            for i in completed if i.content_difficulty
        ) / len(completed)
        
        if avg_level >= 3.5:
            return "expert"
        elif avg_level >= 2.5:
            return "advanced"
        elif avg_level >= 1.5:
            return "intermediate"
        else:
            return "beginner"
    
    def _infer_learning_style(self, interactions: List[ContentInteraction]) -> LearningStyleEnum:
        """Infer learning style from content type preferences."""
        format_engagement = Counter()
        
        for interaction in interactions:
            if interaction.content_type and interaction.completion_percentage >= 50:
                format_engagement[interaction.content_type.lower()] += 1
        
        if not format_engagement:
            return LearningStyleEnum.BALANCED
        
        top_format = format_engagement.most_common(1)[0][0]
        
        # Map formats to learning styles
        style_map = {
            "video": LearningStyleEnum.VISUAL,
            "podcast": LearningStyleEnum.AUDITORY,
            "article": LearningStyleEnum.READING,
            "tutorial": LearningStyleEnum.KINESTHETIC,
            "documentation": LearningStyleEnum.READING,
        }
        
        return style_map.get(top_format, LearningStyleEnum.BALANCED)
    
    def _sync_interaction_with_knowledge_graph(
        self,
        user_id: int,
        content_tags: List[str],
        content_difficulty: Optional[str],
        completion_percentage: int,
        interaction_type: InteractionTypeEnum
    ) -> None:
        """
        Sync content interaction with knowledge graph and learning paths.
        Updates mastery levels for concepts based on content engagement.
        """
        if not content_tags:
            return
        
        # Import here to avoid circular dependencies
        from app.features.concept.service import ConceptService
        from app.features.users.knowledge.service import UserKnowledgeService
        
        # Calculate mastery increment based on difficulty and completion
        mastery_increment = self._calculate_mastery_increment(
            content_difficulty,
            completion_percentage,
            interaction_type
        )
        
        if mastery_increment <= 0:
            return
        
        # Get services
        concept_service = ConceptService()
        knowledge_service = UserKnowledgeService()
        
        # Get all concepts in the knowledge graph
        try:
            all_concept_uris = concept_service.get_all_concepts()
        except Exception as e:
            logger.error(f"Failed to list concepts from KG: {e}")
            return
        
        # Extract concept IDs from URIs
        all_concept_ids = [str(uri).split("#")[-1] for uri in all_concept_uris]
        
        # Map content tags to concepts (case-insensitive matching)
        content_tags_lower = [tag.lower().replace(' ', '_') for tag in content_tags]
        matched_concept_ids = []
        
        for concept_id in all_concept_ids:
            concept_name_lower = concept_id.lower()
            # Check if concept name matches any tag or tag matches concept name
            for tag in content_tags_lower:
                if (tag in concept_name_lower or 
                    concept_name_lower in tag or
                    self._is_similar_concept(tag, concept_name_lower)):
                    matched_concept_ids.append(concept_id)
                    break
        
        if not matched_concept_ids:
            logger.info(f"No concepts matched for tags: {content_tags}")
            return
        
        # Determine target mastery state based on increment
        # Higher increments (>0.1) = mark as known
        # Medium increments (0.05-0.1) = mark as learning
        # Lower increments (<0.05) = mark as learning
        target_state = "known" if mastery_increment >= 0.1 else "learning"
        
        # Update mastery for matched concepts
        updated_count = 0
        for concept_id in matched_concept_ids:
            try:
                # Check current state
                known_concepts = knowledge_service.get_user_known_concepts(str(user_id))
                learning_concepts = knowledge_service.get_user_learning_concepts(str(user_id))
                
                known_ids = {str(uri).split("#")[-1] for uri in known_concepts}
                learning_ids = {str(uri).split("#")[-1] for uri in learning_concepts}
                
                # Update state if needed
                if target_state == "known" and concept_id not in known_ids:
                    knowledge_service.mark_concept_as_known(str(user_id), concept_id)
                    updated_count += 1
                    logger.info(
                        f"Marked concept '{concept_id}' as KNOWN for user {user_id} "
                        f"(increment: {mastery_increment:.3f})"
                    )
                elif target_state == "learning" and concept_id not in known_ids and concept_id not in learning_ids:
                    knowledge_service.mark_concept_as_learning(str(user_id), concept_id)
                    updated_count += 1
                    logger.info(
                        f"Marked concept '{concept_id}' as LEARNING for user {user_id} "
                        f"(increment: {mastery_increment:.3f})"
                    )
                elif concept_id in learning_ids and target_state == "known":
                    # Promote from learning to known
                    knowledge_service.mark_concept_as_known(str(user_id), concept_id)
                    updated_count += 1
                    logger.info(
                        f"Promoted concept '{concept_id}' from LEARNING to KNOWN for user {user_id}"
                    )
                
            except Exception as e:
                logger.error(f"Failed to update concept {concept_id}: {e}")
                continue
        
        if updated_count > 0:
            logger.info(
                f"Successfully updated {updated_count} concepts for user {user_id} "
                f"from content interaction"
            )
            
            # Sync learning path progress with updated knowledge graph
            try:
                self._sync_learning_path_progress(user_id, matched_concept_ids)
            except Exception as e:
                logger.error(f"Failed to sync learning path progress: {e}")
    
    def _calculate_mastery_increment(
        self,
        difficulty: Optional[str],
        completion_percentage: int,
        interaction_type: InteractionTypeEnum
    ) -> float:
        """
        Calculate how much to increment mastery based on content engagement.
        
        Returns:
            Mastery increment (0.0 to 1.0)
        """
        # Base increment based on interaction type
        interaction_weights = {
            InteractionTypeEnum.VIEWED: 0.02,
            InteractionTypeEnum.CLICKED: 0.03,
            InteractionTypeEnum.COMPLETED: 0.15,
            InteractionTypeEnum.BOOKMARKED: 0.05,
            InteractionTypeEnum.SHARED: 0.08,
            InteractionTypeEnum.RATED: 0.05,
        }
        
        base_increment = interaction_weights.get(interaction_type, 0.03)
        
        # Adjust based on completion percentage
        completion_multiplier = completion_percentage / 100.0
        
        # Adjust based on difficulty (harder content = more learning)
        difficulty_multipliers = {
            "beginner": 0.8,
            "intermediate": 1.0,
            "advanced": 1.3,
            "expert": 1.5
        }
        
        difficulty_multiplier = difficulty_multipliers.get(
            difficulty.lower() if difficulty else "intermediate",
            1.0
        )
        
        # Calculate final increment
        increment = base_increment * completion_multiplier * difficulty_multiplier
        
        # Cap at reasonable maximum (0.2 per interaction)
        return min(0.2, increment)
    
    def _is_similar_concept(self, tag: str, concept_name: str) -> bool:
        """
        Check if a tag and concept name are similar enough to match.
        
        Uses simple heuristics:
        - Checks for common word roots
        - Handles plural/singular forms
        """
        # Remove common suffixes
        tag_root = tag.rstrip('s').rstrip('ing').rstrip('ed')
        concept_root = concept_name.rstrip('s').rstrip('ing').rstrip('ed')
        
        # Check if roots match
        if tag_root == concept_root:
            return True
        
        # Check for common programming language variations
        common_variations = {
            'js': 'javascript',
            'py': 'python',
            'ts': 'typescript',
            'react': 'reactjs',
            'vue': 'vuejs',
            'node': 'nodejs',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'db': 'database',
            'api': 'apis',
        }
        
        tag_normalized = common_variations.get(tag_root, tag_root)
        concept_normalized = common_variations.get(concept_root, concept_root)
        
        return tag_normalized == concept_normalized or tag_normalized in concept_normalized or concept_normalized in tag_normalized
    
    def _sync_learning_path_progress(self, user_id: int, concept_ids: List[str]) -> None:
        """
        Sync learning path progress after knowledge graph updates.
        Updates mastery levels for all active learning paths containing the updated concepts.
        """
        from app.features.learning_path.models import LearningPath
        from app.features.learning_path.progress_service import LearningPathProgressService
        
        # Find all active learning paths for the user
        active_paths = self.db.query(LearningPath).filter(
            LearningPath.user_id == user_id,
            LearningPath.is_archived == False
        ).all()
        
        if not active_paths:
            logger.debug(f"No active learning paths found for user {user_id}")
            return
        
        progress_service = LearningPathProgressService(self.db)
        total_updates = 0
        
        for path in active_paths:
            # Check if any of the updated concepts are in this learning path
            path_concepts = set()
            
            # Extract concept names from learning path structure
            # The structure is a list of steps, each with concept_id
            if hasattr(path, 'structure') and path.structure:
                for step in path.structure:
                    if isinstance(step, dict) and 'concept_id' in step:
                        path_concepts.add(step['concept_id'])
            
            # Match concept IDs (case-insensitive)
            matched_concepts = []
            for concept_id in concept_ids:
                for path_concept in path_concepts:
                    if (concept_id.lower() == path_concept.lower() or
                        concept_id.lower().replace('_', ' ') == path_concept.lower().replace('_', ' ')):
                        matched_concepts.append(path_concept)
                        break
            
            if matched_concepts:
                logger.info(
                    f"Syncing {len(matched_concepts)} concepts in learning path "
                    f"'{path.conversation_thread_id}' for user {user_id}"
                )
                
                # Update progress for each matched concept
                for concept_name in matched_concepts:
                    try:
                        progress_service.update_concept_progress(
                            user_id=user_id,
                            thread_id=path.conversation_thread_id,
                            concept_name=concept_name,
                            completed_content=True  # Mark as completed content interaction
                        )
                        total_updates += 1
                    except Exception as e:
                        logger.error(f"Failed to update progress for concept '{concept_name}': {e}")
        
        if total_updates > 0:
            logger.info(
                f"Successfully synced {total_updates} learning path progress records "
                f"for user {user_id}"
            )

    
    def build_user_profile(self, user_id: int) -> UserProfile:
        """
        Build a UserProfile for content discovery from stored preferences.
        This combines explicit preferences with learned behavior.
        """
        prefs = self.get_or_create_preferences(user_id)
        
        return UserProfile(
            user_id=str(user_id),
            knowledge_areas=prefs.knowledge_areas or {},
            learning_goals=prefs.learning_goals or [],
            preferred_formats=prefs.preferred_formats or [],
            available_time_daily=prefs.available_time_daily or 60,
            learning_style=prefs.learning_style.value if prefs.learning_style else "balanced"
        )
    
    def get_insights(self, user_id: int) -> Dict[str, Any]:
        """Get insights about user's learning patterns."""
        prefs = self.get_or_create_preferences(user_id)
        
        # Get interaction stats
        total_interactions = self.db.query(func.count(ContentInteraction.id)).filter(
            ContentInteraction.user_id == user_id
        ).scalar()
        
        completed_count = self.db.query(func.count(ContentInteraction.id)).filter(
            ContentInteraction.user_id == user_id,
            ContentInteraction.completion_percentage >= 80
        ).scalar()
        
        avg_rating = self.db.query(func.avg(ContentInteraction.rating)).filter(
            ContentInteraction.user_id == user_id,
            ContentInteraction.rating.isnot(None)
        ).scalar()
        
        # Recent learning streak
        recent_days = self.db.query(
            func.date(ContentInteraction.timestamp).label('day')
        ).filter(
            ContentInteraction.user_id == user_id
        ).distinct().order_by(desc('day')).limit(7).all()
        
        return {
            "preferences": {
                "preferred_formats": prefs.preferred_formats,
                "learning_style": prefs.learning_style.value if prefs.learning_style else "balanced",
                "preferred_difficulty": prefs.preferred_difficulty,
                "available_time_daily": prefs.available_time_daily,
                "knowledge_areas": prefs.knowledge_areas,
                "learning_goals": prefs.learning_goals,
                "auto_evolve": bool(prefs.auto_evolve)
            },
            "stats": {
                "total_interactions": total_interactions or 0,
                "completed_count": completed_count or 0,
                "completion_rate": round((completed_count / total_interactions * 100) if total_interactions else 0, 1),
                "average_rating": round(float(avg_rating), 2) if avg_rating else None,
                "learning_streak_days": len(recent_days)
            },
            "last_updated": prefs.updated_at.isoformat() if prefs.updated_at else None
        }
