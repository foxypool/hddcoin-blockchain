import React from 'react';
import { SvgIcon, SvgIconProps } from '@material-ui/core';
import { ReactComponent as HDDappsUtilityHeroIcon } from './images/HDDappsUtilityHero.svg';

export default function HDDappsUtilityHero(props: SvgIconProps) {
  return <SvgIcon component={HDDappsUtilityHeroIcon} viewBox="0 0 48 48" {...props} />;
}
