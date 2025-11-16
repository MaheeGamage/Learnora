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
    segment: 'evaluate',
    title: 'Evaluate'
  }
];