import React, { useState, forwardRef } from 'react';
import { Trans } from '@lingui/macro';
import { Button, CardStep, Select, Flex, Loading } from '@hddcoin/core';
import {
  Box,
  Grid,
  FormControl,
  InputLabel,
  MenuItem,
  Typography,
} from '@material-ui/core';
import { useFormContext } from 'react-hook-form';
import usePlotNFTs from '../../../hooks/usePlotNFTs';
import PlotNFTName from '../../plotNFT/PlotNFTName';
import PlotNFTSelectPool from '../../plotNFT/select/PlotNFTSelectPool';
import Plotter from '../../../types/Plotter';

type Props = {
  step: number;
  plotter: Plotter;
};

const PlotAddNFT = forwardRef((props: Props, ref) => {
  const { step } = props;
  const { nfts, external, loading } = usePlotNFTs();
  const [showCreatePlotNFT, setShowCreatePlotNFT] = useState<boolean>(false);
  const { setValue } = useFormContext();

  const hasNFTs = !!nfts?.length || !!external?.length;

  function handleJoinPool() {
    setShowCreatePlotNFT(true);
    setValue('createNFT', true);
  }

  function handleCancelPlotNFT() {
    setShowCreatePlotNFT(false);
    setValue('createNFT', false);
  }

  if (showCreatePlotNFT) {
    return (
      <PlotNFTSelectPool
        step={step}
        onCancel={handleCancelPlotNFT}
        ref={ref}
        title={<Trans>Create a Plot NFT</Trans>}
        description={
          <Trans>
            Join a pool and get consistent HDD farming rewards. The average
            returns are the same, but it is much less volatile.
          </Trans>
        }
      />
    );
  }

  return (
    <CardStep
      step={step}
      title={
        <Flex gap={1} alignItems="baseline">
          <Box>
            <Trans>Join a Pool</Trans>
          </Box>
          <Typography variant="body1" color="textSecondary">
            <Trans>(NFT Pooling not supported)</Trans>
          </Typography>
        </Flex>
      }
    >
      {loading && <Loading center />}

      {!loading && hasNFTs && (
        <>
          <Typography variant="subtitle1">
            <Trans>
              Select your Plot NFT from the dropdown or create a new one.
            </Trans>
          </Typography>

          <Grid spacing={2} direction="column" container>
            <Grid xs={12} md={8} lg={6} item>
              <FormControl variant="filled" fullWidth>
                <InputLabel required>
                  <Trans>Select your Plot NFT</Trans>
                </InputLabel>
                <Select name="p2_singleton_puzzle_hash">
                  <MenuItem value="">
                    <em>
                      <Trans>None</Trans>
                    </em>
                  </MenuItem>
                  {nfts?.map((nft) => {
                    const {
                      pool_state: { p2_singleton_puzzle_hash },
                    } = nft;

                    return (
                      <MenuItem
                        value={p2_singleton_puzzle_hash}
                        key={p2_singleton_puzzle_hash}
                      >
                        <PlotNFTName nft={nft} />
                      </MenuItem>
                    );
                  })}
                  {external?.map((nft) => {
                    const {
                      pool_state: { p2_singleton_puzzle_hash },
                    } = nft;

                    return (
                      <MenuItem
                        value={p2_singleton_puzzle_hash}
                        key={p2_singleton_puzzle_hash}
                      >
                        <PlotNFTName nft={nft} />
                      </MenuItem>
                    );
                  })}
                </Select>
              </FormControl>
            </Grid>

            <Grid xs={12} md={8} lg={6} item>
              <Button onClick={handleJoinPool} variant="outlined">
                <Trans>+ Add New Plot NFT</Trans>
              </Button>
            </Grid>
          </Grid>
        </>
      )}

      {!loading && !hasNFTs && (
        <>
          <Typography variant="subtitle1">
            <Trans> 
			  HDDcoin supports pooling for OG plots. Pooling with NFT plots, 
			  which were not created with the HDDcoin Client is not yet supported. 
			  Please visit https://hddcoin/pooling/ to learn more, 
			  to check out currently supported OG pools, and to find out when support for 
			  NFT pooling with plots not created with the HDDcoin Client will become available.			  
            </Trans>
          </Typography>
          {/*  // Hide Join Pool Button
          <Box>
            <Button onClick={handleJoinPool} variant="contained">
              <Trans>Join a Pool</Trans>
            </Button>
          </Box>
		  */} 
        </>
      )}
    </CardStep>
  );
});

export default PlotAddNFT;
