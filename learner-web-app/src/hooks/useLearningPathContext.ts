import { useContext } from 'react';
import { LearningPathContext, type LearningPathContextType } from '../contexts/LearningPathContextDef';

/**
 * Hook to access LearningPath context
 * Must be used within LearningPathContextProvider
 */
export function useLearningPathContext(): LearningPathContextType {
  const context = useContext(LearningPathContext);
  if (!context) {
    throw new Error('useLearningPathContext must be used within LearningPathContextProvider');
  }
  return context;
}
