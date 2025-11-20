import React from 'react';
import { 
    Card, 
    CardContent, 
    CardMedia, 
    Typography, 
    CardActions, 
    Button, 
    Chip, 
    Stack, 
    Avatar,
    Box
} from '@mui/material';
import type { FeedContent } from '../types';
import ArticleIcon from '@mui/icons-material/Article';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';

interface FeedContentCardProps {
    item: FeedContent;
}

const FeedContentCard: React.FC<FeedContentCardProps> = ({ item }) => {
    return (
        <Card sx={{ maxWidth: '100%', mb: 2, borderRadius: 2, boxShadow: 3 }}>
            <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                    <ArticleIcon />
                </Avatar>
                <Box>
                    <Typography variant="subtitle2" color="text.secondary">
                        Recommended for you • {item.topic}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                        {item.source} • {item.publishedDate}
                    </Typography>
                </Box>
            </Box>
            
            {item.imageUrl && (
                <CardMedia
                    component="img"
                    height="194"
                    image={item.imageUrl}
                    alt={item.title}
                />
            )}
            
            <CardContent>
                <Typography variant="h6" gutterBottom component="div">
                    {item.title}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {item.description}
                </Typography>
                
                <Stack direction="row" spacing={1} alignItems="center">
                    {item.readTime && (
                        <Chip 
                            icon={<AccessTimeIcon />} 
                            label={item.readTime} 
                            size="small" 
                            variant="outlined" 
                        />
                    )}
                    <Chip label={item.topic} size="small" color="primary" variant="outlined" />
                </Stack>
            </CardContent>
            
            <CardActions disableSpacing sx={{ justifyContent: 'flex-end', px: 2, pb: 2 }}>
                <Button 
                    variant="contained" 
                    endIcon={<OpenInNewIcon />}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Read Article
                </Button>
            </CardActions>
        </Card>
    );
};

export default FeedContentCard;
