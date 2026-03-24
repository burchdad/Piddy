import React from 'react';

/**
 * Reusable Piddy avatar component — ghost architect branding.
 * Sizes: 'xs' (20px), 'sm' (28px), 'md' (40px), 'lg' (64px), 'xl' (120px)
 */
function PiddyAvatar({ size = 'md', className = '', glow = false, style = {} }) {
  const sizes = { xs: 20, sm: 28, md: 40, lg: 64, xl: 120 };
  const px = sizes[size] || sizes.md;

  return (
    <img
      src="/piddy-avatar.png"
      alt="Piddy"
      className={`piddy-avatar piddy-avatar-${size} ${glow ? 'piddy-avatar-glow' : ''} ${className}`}
      style={{ width: px, height: px, ...style }}
      draggable={false}
    />
  );
}

export default PiddyAvatar;
