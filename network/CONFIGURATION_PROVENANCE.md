# Network configuration provenance

I retain `network/configtx.yaml` as the existing repository configuration.

I preserve the supplied field configuration separately under `network/field/configtx.yaml`.

The current `network/configtx.yaml` defines four organizations, a 2-hour batch timeout and 100 transactions per block. The bootstrap and peer deployment scripts still provision one shared FarmMSP, and the full four-organization configuration has not been established as the historical benchmark configuration. The previously documented 2-second/10-transaction values refer to an earlier repository revision.

I have not established the configuration used for every historical controlled benchmark. I will not label a configuration as deployed without supporting evidence.
