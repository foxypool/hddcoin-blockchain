import React from 'react';
import { SvgIcon, SvgIconProps } from '@material-ui/core';
import { ReactComponent as HDDappsIcon } from './images/hddapps.svg';

export default function HDDapps(props: SvgIconProps) {
  return <SvgIcon component={HDDappsIcon} viewBox="0 0 39 39" {...props} />;
}
