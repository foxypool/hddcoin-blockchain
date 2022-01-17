import React from 'react';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Flex } from '@hddcoin/core';
import { Button, Grid, Typography, Link, Card, Divider } from '@material-ui/core';
import { CardHero } from '@hddcoin/core';
import { HDDappsUtilityHero as HDDappsUtilityHeroIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsUtilityHeroIcon)`
  font-size: 4rem;
`;

export default function HDDappsUtility() {
  const history = useHistory();

   function hddAppsOpenTerminal() {
	history.push('/dashboard/hddapps/utilityterminal');
  }
  
   function hddAppsOpenLogs() {
	history.push('/dashboard/hddapps/utilitylogs');
  }
  
  return (
    <Grid container>
	  <Grid xs={12} md={12} lg={12} item>
	  
        <CardHero>		  
		  
		  <StyledHDDappsIcon color="primary" />		

          <Typography variant="h5">
            <Trans>
              HDDcoin Utility Tools
            </Trans>
          </Typography>	

		  <Divider />		  
		  
		  <Typography variant="body1">
			<Trans>
              Prefer to work in command line? Open a Terminal window with the HDDcoin executable conveniently loaded for your Opearting System. 
			  Want to examine your HDDcoin Client log? Open a window within the Client with your recent logs loaded and updated in real time.  
			</Trans>
		  </Typography>
		  
		  <Flex gap={1}>
            <Button
              onClick={hddAppsOpenTerminal}
              variant="contained"
              color="primary"
              fullWidth
            >
              <Trans>Open HDDcoin Terminal</Trans>
            </Button>
			
            <Button
              onClick={hddAppsOpenLogs}
              variant="outlined"
              color="primary"
              fullWidth
            >
              <Trans>Open HDDcoin Logs</Trans>
            </Button>
          </Flex>
		  
        </CardHero>
      </Grid>
    </Grid>
  );
}
