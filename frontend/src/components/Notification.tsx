import type { FC, SyntheticEvent } from 'react';
import { useState, useEffect } from 'react';
import {
  Snackbar,
  Alert,
  IconButton,
  Collapse,
  Typography,
  Box,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { Notification as NotificationType } from '../contexts/NotificationContext';

interface NotificationProps {
  notification: NotificationType;
  onClose: () => void;
}

export const Notification: FC<NotificationProps> = ({ notification, onClose }) => {
  const [expanded, setExpanded] = useState(false);
  const [show, setShow] = useState(true);
  const [hovered, setHovered] = useState(false);

  useEffect(() => {
    if (!hovered) {
      const timer = setTimeout(() => {
        setShow(false);
        setTimeout(onClose, 300); // Wait for animation to complete
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [hovered, onClose]);

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleClose = (event: SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setShow(false);
    setTimeout(onClose, 300);
  };

  return (
    <Snackbar
      open={show}
      anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <Alert
        severity={notification.type}
        action={
          <Box>
            {notification.details && (
              <IconButton
                size="small"
                onClick={handleExpandClick}
                sx={{ mr: 1 }}
              >
                {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            )}
            <IconButton
              size="small"
              aria-label="close"
              color="inherit"
              onClick={handleClose}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </Box>
        }
        sx={{ width: '100%', maxWidth: 400 }}
      >
        <Typography variant="body2">{notification.message}</Typography>
        <Collapse in={expanded}>
          <Typography variant="body2" sx={{ mt: 1 }}>
            {notification.details}
          </Typography>
        </Collapse>
      </Alert>
    </Snackbar>
  );
};
