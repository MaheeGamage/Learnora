import LinearProgress from '@mui/material/LinearProgress';
import { Outlet, Navigate, useLocation } from 'react-router';
import { DashboardLayout, ThemeSwitcher } from '@toolpad/core/DashboardLayout';
import { PageContainer } from '@toolpad/core/PageContainer';
import { useSession } from '../../common/hooks/useSession';
import { Stack, Tooltip, IconButton, TextField } from '@mui/material';
import { Account } from '@toolpad/core';
import SearchIcon from '@mui/icons-material/Search';
import { ChatPanelWrapper } from '../components/ChatPanel';
import { ConnectedChatWindow } from '../../features/agent/ConnectedChatWindow';

function ToolbarActionsSearch() {
  return (
    <Stack direction="row">
      <Tooltip title="Search" enterDelay={1000}>
        <div>
          <IconButton
            type="button"
            aria-label="search"
            sx={{
              display: { xs: 'inline', md: 'none' },
            }}
          >
            <SearchIcon />
          </IconButton>
        </div>
      </Tooltip>
      <TextField
        label="Search"
        variant="outlined"
        size="small"
        slotProps={{
          input: {
            endAdornment: (
              <IconButton type="button" aria-label="search" size="small">
                <SearchIcon />
              </IconButton>
            ),
            sx: { pr: 0.5 },
          },
        }}
        sx={{ display: { xs: 'none', md: 'inline-block' }, mr: 1 }}
      />
      <ThemeSwitcher />
      <Account />
    </Stack>
  );
}

export default function MainDashboardLayout() {
  const { session, loading } = useSession();
  const location = useLocation();

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
      slots={{
        toolbarActions: ToolbarActionsSearch
      }}
    >
      <ChatPanelWrapper
        defaultOpen={true}
        width={350}
        chatComponent={<ConnectedChatWindow
          agentTitle="AI Learning Assistant"
          initialTopic="Python Programming" // TODO: Get this from user input
        />}
      >
        <PageContainer>
          <Outlet />
        </PageContainer>
      </ChatPanelWrapper>
    </DashboardLayout>
  );
}
