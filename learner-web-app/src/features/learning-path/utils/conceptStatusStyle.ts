import type { ConceptStatus } from './jsonldUtils';

/**
 * Style configuration for concept status
 */
export interface ConceptStatusStyle {
  borderColor: string;
  backgroundColor: string;
  icon: string;
}

/**
 * Get the visual styling for a concept based on its status
 * @param status - The concept status ('known' | 'ready' | 'locked')
 * @returns Style configuration object
 */
export const getConceptStatusStyle = (status?: ConceptStatus): ConceptStatusStyle => {
  switch (status) {
    case 'known':
      return {
        borderColor: '#4caf50',
        backgroundColor: '#e8f5e9',
        icon: '✓',
      };
    case 'ready':
      return {
        borderColor: '#2196f3',
        backgroundColor: '#e3f2fd',
        icon: '🔓',
      };
    case 'locked':
      return {
        borderColor: '#f44336',
        backgroundColor: '#ffebee',
        icon: '🔒',
      };
    default:
      return {
        borderColor: '#e0e0e0',
        backgroundColor: '#ffffff',
        icon: '',
      };
  }
};
