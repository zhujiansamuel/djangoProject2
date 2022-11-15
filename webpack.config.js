const path = require('path');
const { merge } = require('webpack-merge');
const BundleTracker = require('webpack-bundle-tracker');
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const CopyPlugin = require("copy-webpack-plugin");
const StyleLintPlugin = require('stylelint-webpack-plugin')


const baseConfig = {
    entry: {
        'kingbuy': "./static/additionaljs/kingbuy.js", // エントリポイントの分追加が必要
    },
    output: {
        filename: 'js/[name].[fullhash].bundle.js',
        path: path.resolve(__dirname, 'dist'),
    },
    optimization: {
        splitChunks: {
            cacheGroups: {
                commons: {
                    test: /[\\/]node_modules[\\/]/,
                    chunks: 'initial',
                    name: 'vendor',
                },
            },
        },
    },
    module: {
        rules: [
            {
                test: /\.(css|scss)$/,
                use: [MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader'],
            },
            {
                test: /\.(eot|otf|webp|svg|ttf|woff|woff2)(\?.*)?$/,
                use: [
                    {
                        loader: 'file-loader',
                        options: {
                            name: '[name].[ext]',
                            outputPath: 'fonts'
                        }
                    }
                ]
            },
            {
                test: /\.(ico|jpg|jpeg|png|gif)(\?.*)?$/,
                generator: {
                    filename: 'static/img/[name][ext]'
                },
                type: 'asset/resource'
            }
        ],
    },
    plugins: [
        new BundleTracker({
            path: __dirname,
            filename: 'webpack-stats.json',
        }),
        new MiniCssExtractPlugin({
            filename: 'css/[name].[fullhash].bundle.css'
        }),
        new CopyPlugin({
            patterns: [
                { from: "static/img", to: "img" },
            ],
        }),
        new StyleLintPlugin({
            files: ['static/scss/*.scss'],
            syntax: 'scss',
            fix: false
        }),
    ]
};

const devConfig = merge(baseConfig, {
    mode: 'development',
    output: {
        publicPath: 'http://localhost:3000/static/',
    },
    devServer: {
        port: 3000,
        hot: true,
        headers: {
            "Access-Control-Allow-Origin": "*"
        },
        // watchOptions: {
        //     ignored: /node_modules/
        // },
    },
});

const productConfig = merge(baseConfig, {
    mode: 'production',
    output: {
        publicPath: '/static/'
    }
})

module.exports = (env, options) => {
    return options.mode === 'production' ? productConfig : devConfig
}