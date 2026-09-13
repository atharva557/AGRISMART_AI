const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  return {
    entry: {
      // Core bundle - loaded on all pages
      main: './app/static/js/src/main.js',
      // Page-specific bundles
      home: './app/static/js/src/pages/home.js',
      disease: './app/static/js/src/pages/disease.js',
      advisory: './app/static/js/src/pages/advisory.js',
    },
    output: {
      path: path.resolve(__dirname, 'app/static/js/dist'),
      filename: '[name].min.js',
      clean: true,
    },
    module: {
      rules: [
        {
          test: /\.css$/,
          use: [
            MiniCssExtractPlugin.loader,
            'css-loader',
            'postcss-loader',
          ],
        },
      ],
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: '../css/dist/[name].min.css',
      }),
    ],
    optimization: {
      minimizer: [
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: isProduction,
            },
          },
        }),
        new CssMinimizerPlugin(),
      ],
      splitChunks: {
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendor',
            chunks: 'all',
          },
        },
      },
    },
    devtool: isProduction ? 'source-map' : 'eval-source-map',
    watchOptions: {
      ignored: /node_modules/,
    },
  };
};
