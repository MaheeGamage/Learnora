// /**
//  * React Query integration example for LearningPathVisualization
//  * 
//  * This demonstrates how to use the component with @tanstack/react-query
//  */

// import { useQuery } from "@tanstack/react-query";
// import LearningPathVisualization from "./LearningPathVisualization";
// import type { JsonLdDocument } from "jsonld";

// interface LearningPathQueryProps {
//     learningPathId: string;
// }

// /**
//  * Custom hook to fetch learning path data using React Query
//  */
// function useLearningPath(id: string) {
//     return useQuery<JsonLdDocument, Error>({
//         queryKey: ['learningPath', id],
//         queryFn: async () => {
//             const response = await fetch(`/api/learning-paths/${id}`);
//             if (!response.ok) {
//                 throw new Error(`Failed to fetch learning path: ${response.statusText}`);
//             }
//             return response.json();
//         },
//         enabled: !!id,
//         staleTime: 5 * 60 * 1000, // 5 minutes
//         gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
//     });
// }

// /**
//  * Component using React Query to fetch and display learning path
//  */
// export const LearningPathWithReactQuery: React.FC<LearningPathQueryProps> = ({ 
//     learningPathId 
// }) => {
//     const { data, isLoading, error, isError } = useLearningPath(learningPathId);

//     if (isLoading) {
//         return (
//             <div style={{ 
//                 display: 'flex', 
//                 justifyContent: 'center', 
//                 alignItems: 'center', 
//                 height: '500px',
//                 color: '#666'
//             }}>
//                 <div style={{ textAlign: 'center' }}>
//                     <div style={{ 
//                         width: '40px', 
//                         height: '40px', 
//                         border: '4px solid #f3f3f3',
//                         borderTop: '4px solid #FA4F40',
//                         borderRadius: '50%',
//                         animation: 'spin 1s linear infinite',
//                         margin: '0 auto 10px'
//                     }} />
//                     <p>Loading learning path...</p>
//                 </div>
//             </div>
//         );
//     }

//     if (isError) {
//         return (
//             <div style={{ 
//                 padding: '20px', 
//                 backgroundColor: '#ffebee', 
//                 border: '1px solid #ef5350',
//                 borderRadius: '4px',
//                 margin: '20px'
//             }}>
//                 <h3 style={{ color: '#c62828', margin: '0 0 10px 0' }}>
//                     Error Loading Learning Path
//                 </h3>
//                 <p style={{ margin: 0, color: '#d32f2f' }}>
//                     {error?.message || 'An unexpected error occurred'}
//                 </p>
//             </div>
//         );
//     }

//     if (!data) {
//         return (
//             <div style={{ padding: '20px', textAlign: 'center', color: '#666' }}>
//                 <p>No learning path data available</p>
//             </div>
//         );
//     }

//     return (
//         <div style={{ width: '100%', height: '100%' }}>
//             <LearningPathVisualization 
//                 jsonldData={data}
//                 height="600px"
//                 width="100%"
//             />
//         </div>
//     );
// };

// export default LearningPathWithReactQuery;
