// Split the single .tif file into tiled layers of png files
// Move the output_files folder into the assets folder when done

var sharp = require('sharp');

sharp('../assets/Jacksonville SEC.tif')
  .png()
  .tile({
    size: 512
  })
  .toFile('output.dz', function(err, info) {
    // output.dzi is the Deep Zoom XML definition
    // output_files contains 512x512 tiles grouped by zoom level
  });