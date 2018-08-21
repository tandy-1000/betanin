export default {
  downloads: state =>
    state.downloads,
  lines: state => torrentID => {
    return state.lines[torrentID]
  },
  connected: state =>
    state.connected,
  haveDownloads: state =>
    state.downloads.length !== 0
}
