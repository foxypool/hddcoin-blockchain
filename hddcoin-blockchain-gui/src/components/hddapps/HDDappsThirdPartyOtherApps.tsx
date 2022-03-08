import React from 'react';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Flex, Link, CardHero } from '@hddcoin/core';
import { Button, Grid, Typography, Divider } from '@material-ui/core';
import useOpenExternal from '../../hooks/useOpenExternal';
import { HDDappsThirdPartyOtherAppsHero as HDDappsThirdPartyOtherAppsHeroIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsThirdPartyOtherAppsHeroIcon)`
  font-size: 4rem;
`;

export default function HDDappsThirdPartyOtherApps() {
  const history = useHistory();
  const openExternal = useOpenExternal();

  function hddAppsURLbuttonClickThirdPartyApps() {
            openExternal('https://hddcoin.org/pooling/');
        }
		
  return (
    <Grid container>
      <Grid xs={12} md={12} lg={12} item>
        <CardHero>
		
          <StyledHDDappsIcon color="primary" />
		  
		  <Typography variant="h5">
		    <Trans>
			  Third Party App -- Pool
			</Trans>
          </Typography>
		  
		  <Divider />
		  
          <Typography variant="body1">
            <Trans>              
			
			{'We have partnered with Foxy-Pool to offer our farmers the opportunity to smooth out their rewards, with more Pools coming soon. As more developers in the community release applications and services running on the HDDcoin Blockchain, we will highlight them here. '}
			
            </Trans>
          </Typography>
		  	
		  <Flex gap={1}>
            <Button
              onClick={hddAppsURLbuttonClickThirdPartyApps}
              variant="contained"
              color="primary"
              //fullWidth
            >
              <Trans>Join a Pool</Trans>
            </Button>
			
          </Flex>	  
		  
        </CardHero>
      </Grid>
    </Grid>
  );
}
