import React from 'react';
import { SvgIcon, SvgIconProps } from '@material-ui/core';
import { ReactComponent as HODLterminalIcon } from './images/hodlterminal.svg';

export default function HODLterminal(props: SvgIconProps) {
  return <SvgIcon component={HODLterminalIcon} viewBox="0 0 39 39" {...props} />;
}
