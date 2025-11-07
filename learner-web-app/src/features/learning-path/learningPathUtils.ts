/**
 * Helper utilities for creating learning path JSON-LD data
 */

import type { JsonLdDocument } from "jsonld";

export interface CourseNode {
    id: string;
    name: string;
    description?: string;
    prerequisites?: string[];
}

export interface LearningPathData {
    courses: CourseNode[];
}

/**
 * Converts a simple learning path structure to JSON-LD format
 */
export function createLearningPathJsonLd(data: LearningPathData): JsonLdDocument {
    const context = {
        "@vocab": "http://schema.org/",
        "name": "http://schema.org/name",
        "description": "http://schema.org/description",
        "prerequisite": {
            "@id": "http://schema.org/prerequisite",
            "@type": "@id"
        }
    };

    const courseMap = new Map<string, CourseNode>();
    for (const course of data.courses) {
        courseMap.set(course.id, course);
    }

    const buildCourseNode = (courseId: string, visited = new Set<string>()): JsonLdDocument | null => {
        if (visited.has(courseId)) {
            // Avoid circular dependencies
            return { "@id": courseId };
        }

        const course = courseMap.get(courseId);
        if (!course) return null;

        visited.add(courseId);

        const node: JsonLdDocument = {
            "@id": courseId,
            "@type": "Course",
            "name": course.name,
        };

        if (course.description) {
            node["description"] = course.description;
        }

        if (course.prerequisites && course.prerequisites.length > 0) {
            node["prerequisite"] = course.prerequisites
                .map(prereqId => buildCourseNode(prereqId, new Set(visited)))
                .filter((n): n is JsonLdDocument => n !== null);
        }

        return node;
    };

    // Build graph starting from courses without prerequisites
    const rootCourses = data.courses.filter(
        course => !course.prerequisites || course.prerequisites.length === 0
    );

    if (rootCourses.length === 1) {
        return {
            "@context": context,
            ...buildCourseNode(rootCourses[0].id)!
        };
    }

    // Multiple root courses - use @graph
    return {
        "@context": context,
        "@graph": data.courses.map(course => buildCourseNode(course.id)).filter((n): n is JsonLdDocument => n !== null)
    };
}

/**
 * Example: Create a simple linear learning path
 */
export function createLinearPath(courses: Array<{ id: string; name: string; description?: string }>): JsonLdDocument {
    const learningPath: LearningPathData = {
        courses: courses.map((course, index) => ({
            ...course,
            prerequisites: index > 0 ? [courses[index - 1].id] : []
        }))
    };

    return createLearningPathJsonLd(learningPath);
}

/**
 * Example usage:
 * 
 * const path = createLinearPath([
 *   { id: "html", name: "HTML Basics" },
 *   { id: "css", name: "CSS Fundamentals" },
 *   { id: "js", name: "JavaScript" },
 *   { id: "react", name: "React" }
 * ]);
 */
