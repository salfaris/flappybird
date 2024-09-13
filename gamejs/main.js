/**
 * @fileoverview
 * Flappy Bird JS port.
 */
var gamejs = require('gamejs');
var pixelcollision = require('gamejs/pixelcollision');
var graphics = require('gamejs/graphics');

const colorWhite = 'rgb(255, 255, 255)';


const getAsset = (path) => {
    const assets_dir = "../assets/";
    return assets_dir + path;
};

const loadImage = (path) => {
    return gamejs.image.load(path);
};


const main = () => {
    const birdImgs = [
        loadImage(getAsset("bird1.png")),
        loadImage(getAsset("bird2.png")),
        loadImage(getAsset("bird3.png")),
    ]
    const bgImg = loadImage(getAsset("bg.png"));
    const pipeImg = loadImage(getAsset("pipe.png"));
    const baseImg = loadImage(getAsset("base.png"));
   
    // set resolution & title
   var display = gamejs.display.getSurface();
};

gamejs.preload([
    getAsset("bird1.png"),
    getAsset("bird2.png"),
    getAsset("bird3.png"),
    getAsset("pipe.png"),
    getAsset("base.png"),
    getAsset("bg.png"),
 ]);
// gamejs.ready will call your main function
// once all components and resources are ready.
gamejs.ready(main);