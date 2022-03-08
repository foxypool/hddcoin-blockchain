import React from 'react';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Flex, Link, CardHero } from '@hddcoin/core';
import { Button, Grid, Typography, Divider } from '@material-ui/core';
import useOpenExternal from '../../hooks/useOpenExternal';
import { HDDappsThirdPartyHDDBetHero as HDDappsThirdPartyHDDBetHeroIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsThirdPartyHDDBetHeroIcon)`
  font-size: 4rem;
`;

export default function HDDappsThirdPartyHDDBet() {
  const history = useHistory();
  const openExternal = useOpenExternal();

  function hddAppsURLbuttonClickHDDBet() {
            openExternal('https://hddcoin.bet/');
        }
		
  return (
    <Grid container>
      <Grid xs={12} md={12} lg={12} item>
        <CardHero>
		
          <StyledHDDappsIcon color="primary" />
		  
		  <Typography variant="h5">
		    <Trans>
			  Third Party App -- Bet
			</Trans>
          </Typography>
		  
		  <Divider />
		  
          <Typography variant="body1">
            <Trans>              
			
			{'"Bet on HDDcoins" is a betting service offered to the community by HDDcoin Bet. This is a non-affiliated, third-party application built on top of the HDDcoin Blockchain. Visit their website to learn about the Project or play for a chance to win the Jackpot. '}
			
			  <Link
                target="_blank"
                href="https://hddcoin.bet/"
              >
                Learn more
			 </Link>
					
            </Trans>
          </Typography>
		  	
		  <Flex gap={1}>
            <Button
              onClick={hddAppsURLbuttonClickHDDBet}
              variant="contained"
              color="primary"
              //fullWidth
            >
              <Trans>Bet on HDDcoins</Trans>
            </Button>
			
          </Flex>	  
		  
        </CardHero>
      </Grid>
    </Grid>
  );
}
