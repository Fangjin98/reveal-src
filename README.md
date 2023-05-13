# Code of Reveal

## Data

Reveal use tabel `instance_events` in [Google cluster dataset](https://github.com/google/cluster-data/blob/master/ClusterData2019.md).

```powershell
gsutil cp gs://clusterdata_2019_a/instance_events-000000000000.json.gz <destination dir>
```

## Directory structure

- src
  - elements: models of ecn, user, vnf
  - constant.py: configs
  - reveal.py: the implementation of reveal algorithms
- data: contains the vnf cost, ecn capacity, and the results of different lp.