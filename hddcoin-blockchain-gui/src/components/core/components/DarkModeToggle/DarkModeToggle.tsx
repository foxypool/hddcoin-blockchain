import React from 'react';
import useDarkMode from 'use-dark-mode';
import { IconButton } from '@material-ui/core';
import { Brightness4, Brightness7 } from '@material-ui/icons';
import isElectron from 'is-electron';

export default function DarkModeToggle() {
  const { toggle, value: darkMode } = useDarkMode();

  function handleClick() {
    toggle();
    if (isElectron()) {
      const { nativeTheme } = window.require('@electron/remote');
      nativeTheme.themeSource = darkMode ? 'dark' : 'light';
    }
  }

  return (
    <IconButton color="inherit" onClick={handleClick}>
      {darkMode ? <Brightness7 /> : <Brightness4 />}
    </IconButton>
  );
}
