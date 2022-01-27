import React from 'react';
import styled from 'styled-components';
import { Trans } from '@lingui/macro';
import { useHistory } from 'react-router-dom';
import { Flex, Link, CardHero } from '@hddcoin/core';
import { Button, Grid, Typography, Divider } from '@material-ui/core';
import useOpenExternal from '../../hooks/useOpenExternal';
import { HDDappsNFTMarketPlaceHero as HDDappsNFTMarketPlaceHeroIcon } from '@hddcoin/icons';

const StyledHDDappsIcon = styled(HDDappsNFTMarketPlaceHeroIcon)`
  font-size: 4rem;
`;

export default function HDDappsNFTMarketPlace() {
  const history = useHistory();
  const openExternal = useOpenExternal();

  function hddAppsURLbuttonClickNFT() {
            openExternal('https://hddcoin.org/nft/');
        }
  
  return (
    <Grid container>
      <Grid xs={12} md={12} lg={12} item>
        <CardHero>
		
          <StyledHDDappsIcon color="primary" />
		  
		  <Typography variant="h5">
		    <Trans>
			  HDDcoin NFT Marketplace 
			</Trans>
          </Typography>
		  
		  <Divider />
		  
          <Typography variant="body1">
            <Trans>
			{'The HDDcoin NFT Marketplace offers our community, artists and investors a platform to buy and sell unique digital assets secured and publicly verifiable on the blockchain. This includes art, audio/music, video, virtual worlds and other digital files. '} 
			  <Link
                target="_blank"
                href="https://hddcoin.org/nft/"
              >
                Learn more
			 </Link>
            </Trans>
          </Typography>

		  <Flex gap={1}>
            <Button
              onClick={hddAppsURLbuttonClickNFT}
              variant="contained"
              color="primary"
              // fullWidth
            >
              <Trans>Visit NFT Marketplace</Trans>
            </Button>
		  </Flex>		  
		 	
        </CardHero>
      </Grid>
    </Grid>
  );
}
