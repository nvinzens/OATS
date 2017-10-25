install lftp on master.minion:
  local.pkg.install:
    - tgt: 'master'
    - arg:
      - lftp
