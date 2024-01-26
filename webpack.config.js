const path = require('path');

module.exports = {
  mode: 'development', // 'production' for production builds
  entry: './nginx/html/js/index.js', // Entry point set to index.js

  output: {
    filename: 'bundle.js', // Output bundle file name
    path: path.resolve(__dirname, 'nginx/html/dist'), // Output directory
  },


  module: {
    rules: [
      {
        test: /\.js$/, // Rule for JavaScript files
        exclude: /node_modules/, // Exclude node_modules
        use: {
          loader: 'babel-loader', // Use babel-loader for transpiling
          options: {
            presets: ['@babel/preset-env'], // Preset for modern JavaScript
          },

        },



      },
    ],
  },
};
