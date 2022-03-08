import React from 'react';
import { Route, Switch, useRouteMatch } from 'react-router-dom';
import LayoutMain from '../layout/LayoutMain';
import { Trans } from '@lingui/macro';
import { Flex } from '@hddcoin/core';
import { Grid, Typography } from '@material-ui/core';

import HDDappsHODL from './HDDappsHODL';
import HDDappsOnlineStore from './HDDappsOnlineStore';
import HDDappsNFTMarketPlace from './HDDappsNFTMarketPlace';
import HDDappsExchangeTrading from './HDDappsExchangeTrading';
import HDDappsUtility from './HDDappsUtility';
import HDDappsApplications from './HDDappsApplications';
import HDDappsHODLTerminal from './HDDappsHODLTerminal';
import HDDappsUtilityTerminal from './HDDappsUtilityTerminal';
import HDDappsUtilityLogs from './HDDappsUtilityLogs';
import HDDappsThirdPartyHDDBet from './HDDappsThirdPartyHDDBet';
import HDDappsThirdPartyOtherApps from './HDDappsThirdPartyOtherApps';
import { HDDappsHeaderTarget } from './HDDappsHeader';
import { HDDappsHeaderSource } from './HDDappsHeader';

export default function HDDapps() {
	
  const { path } = useRouteMatch();

  return (
  
    <LayoutMain 
		
      title={
        <>
          <Trans>HDDcoin Applications and Utilities</Trans>
		  <HDDappsHeaderTarget />
        </>
      }
	>	
	
		<>	
		<Flex flexDirection="column" gap={1} alignItems="center">
		
			<Switch>
			  
			  <Route path={path} exact>
				<div>
				
				  <Grid container spacing={4} alignItems="stretch">
				  
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsHODL headerTag={HDDappsHeaderSource} />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsOnlineStore headerTag={HDDappsHeaderSource} />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsNFTMarketPlace headerTag={HDDappsHeaderSource} />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsExchangeTrading headerTag={HDDappsHeaderSource} />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsUtility headerTag={HDDappsHeaderSource} />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsApplications headerTag={HDDappsHeaderSource} />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsThirdPartyHDDBet headerTag={HDDappsHeaderSource} />
					</Grid>
					
					<Grid item xs={12} sm={6} md={6}>
					  <HDDappsThirdPartyOtherApps headerTag={HDDappsHeaderSource} />
					</Grid>
					
				  </Grid>
				  
				</div>

			  </Route>
			  
			  <Route path={`${path}/hodlterminal`} exact>
				<HDDappsHODLTerminal />
			  </Route>
			  
			  <Route path={`${path}/utilityterminal`} exact>
				<HDDappsUtilityTerminal />
			  </Route>
			  
			  <Route path={`${path}/utilitylogs`} exact>
				<HDDappsUtilityLogs />
			  </Route>
			  
			</Switch>

		</Flex>	     
		</> 
	 
    </LayoutMain>
  );
}
