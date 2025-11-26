import type { Navigation } from '@toolpad/core';
// import DashboardIcon from '@mui/icons-material/Dashboard';
import HomeIcon from '@mui/icons-material/Home';
import RouteIcon from '@mui/icons-material/Route';
import SchoolIcon from '@mui/icons-material/School';
import QuestionMarkIcon from '@mui/icons-material/QuestionMark';

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
    title: 'Learning Paths',
    icon: <RouteIcon />,
  },
  {
    segment: 'content',
    title: 'Content',
    icon: <SchoolIcon />,
  },
  {
    segment: 'evaluate',
    title: 'Evaluate',
    icon: <QuestionMarkIcon />,
  },
];