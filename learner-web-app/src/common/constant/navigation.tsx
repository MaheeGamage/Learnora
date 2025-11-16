import type { Navigation } from '@toolpad/core';
// import DashboardIcon from '@mui/icons-material/Dashboard';
import HomeIcon from '@mui/icons-material/Home';
// import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';

export const NAVIGATION: Navigation = [
  {
    title: 'LEARNING-PATH-SELECTOR',
  },
  {
    kind: 'divider'
  },
  {
    title: 'Home',
    icon: <HomeIcon />,
  },
  {
    segment: 'learning-path',
    title: 'Learning Path'
  },
  {
    segment: 'content',
    title: 'Content'
  },
  {
    segment: 'evaluate',
    title: 'Evaluate'
  },
];