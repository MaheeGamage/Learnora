import LinearProgress from '@mui/material/LinearProgress';
import { Outlet, Navigate, useLocation } from 'react-router';
import { DashboardLayout, DashboardSidebarPageItem } from '@toolpad/core/DashboardLayout';
import { PageContainer } from '@toolpad/core/PageContainer';
import { useSession } from '../../common/hooks/useSession';
import { Stack, IconButton, ListItem } from '@mui/material';
import { ChatPanelWrapper } from '../components/ChatPanel';
import { ConnectedChatWindow } from '../../features/agent/ConnectedChatWindow';
import SidebarFooterAccount, { ToolbarAccountOverride } from '../components/SidebarFooterAccount';
// import LearningPathSelector from '../components/LearningPathSelector';
import type { NavigationPageItem } from '@toolpad/core/AppProvider';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { useCallback } from 'react';
import LearningPathSelector from '../../features/learning-path/component/LearningPathSelector';
import { useLearningPathContext } from '../../hooks/useLearningPathContext';

function CustomActions() {
  return (
    <Stack direction="row" alignItems="center">
      {/* <ThemeSwitcher /> */}
      <ToolbarAccountOverride />
    </Stack>
  );
}

function CustomPageItem({
  item,
  mini,
}: {
  item: NavigationPageItem;
  mini: boolean;
}) {
  const { learningPaths, activeLearningPath, setActiveLearningPath } = useLearningPathContext();

  return (
    <ListItem
      sx={(theme) => ({
        color: theme.palette.secondary.main,
        overflowX: 'hidden',
      })}
    >
      {mini ? (
        <IconButton
          aria-label="custom"
          sx={(theme) => ({
            color: theme.palette.secondary.main,
          })}
        >
          <AutoAwesomeIcon />
        </IconButton>
      ) : (
        // <ListItemButton>
        //   <ListItemIcon
        //     sx={(theme) => ({
        //       color: theme.palette.secondary.main,
        //     })}
        //   >
        //     <AutoAwesomeIcon />
        //   </ListItemIcon>
        //   <ListItemText
        //     primary={item.title}
        //     sx={{
        //       whiteSpace: 'nowrap',
        //     }}
        //   />
        // </ListItemButton>
        // <LearningPathSelector />
        <LearningPathSelector
          learningPaths={learningPaths}
          selectedPathId={activeLearningPath ? activeLearningPath.id : null}
          onChange={(id) => setActiveLearningPath(id)}
        />
      )}
    </ListItem>
  );
}

export default function MainDashboardLayout() {
  const { session, loading } = useSession();
  const location = useLocation();

  const renderPageItem = useCallback(
    (item: NavigationPageItem, { mini }: { mini: boolean }) => {
      if (item.title === 'LEARNING-PATH-SELECTOR') {
        return <CustomPageItem item={item} mini={mini} />;
      }

      return <DashboardSidebarPageItem item={item} />;
    }, []);

  if (loading) {
    return (
      <div style={{ width: '100%' }}>
        <LinearProgress />
      </div>
    );
  }

  if (!session) {
    // Add the `callbackUrl` search parameter
    const redirectTo = `/sign-in?callbackUrl=${encodeURIComponent(location.pathname)}`;
    return <Navigate to={redirectTo} replace />;
  }

  return (
    <DashboardLayout
      renderPageItem={renderPageItem}
      slots={{
        toolbarActions: CustomActions,
        sidebarFooter: SidebarFooterAccount,
      }}
    >
      <ChatPanelWrapper
        defaultOpen={true}
        width={360}
        chatComponent={<ConnectedChatWindow
          agentTitle="AI Learning Assistant"
        />}
      >
        <PageContainer title=''>
          <Outlet />
        </PageContainer>
      </ChatPanelWrapper>
    </DashboardLayout>
  );
}
