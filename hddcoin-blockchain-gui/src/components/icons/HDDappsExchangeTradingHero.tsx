import React from 'react';
import { SvgIcon, SvgIconProps } from '@material-ui/core';
import { ReactComponent as HDDappsExchangeTradingHeroIcon } from './images/HDDappsExchangeTradingHero.svg';

export default function HDDappsExchangeTradingHero(props: SvgIconProps) {
  return <SvgIcon component={HDDappsExchangeTradingHeroIcon} viewBox="0 0 60 60" {...props} />;
}
