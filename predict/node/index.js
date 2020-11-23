const MOBILENSWFNET_MODEL_PATH = 'https://raw.githubusercontent.com/nmurray1984/MobileNSFW/master/trained_models/nsfw_v0.3-js/model.json';
const IMAGE_SIZE = 224;

const tf = require('@tensorflow/tfjs-node');
const got = require('got');
const { createCanvas, loadImage } = require('canvas')
//good bmp for consistent inputs
//const url = 'http://eeweb.poly.edu/~yao/EL5123/image/lena_gray.bmp';

const url = "https://thedoctorwhosite.co.uk/wp-images/tardis/console-room-season-21/doors-open.jpg";

async function getImagePixels(imageUrl) {
    const image = await loadImage(imageUrl)
    const canvas = createCanvas(image.naturalWidth, image.naturalHeight);
    const context = canvas.getContext('2d')
    context.drawImage(image, 0, 0);
    const imgCanvas = tf.browser.fromPixels(canvas);
    return imgCanvas;
}

async function loadModel() {
    const model = await tf.loadGraphModel(MOBILENSWFNET_MODEL_PATH);
    return model;
}

async function inference(imageUrl) {
    const model = await loadModel();

    const fullSizeImage = await getImagePixels(url);
    const img = tf.image.resizeBilinear(fullSizeImage, [IMAGE_SIZE, IMAGE_SIZE]);
    const offset = tf.scalar(255);
    const normalized = img.div(offset);
    const batched = normalized.reshape([1, IMAGE_SIZE, IMAGE_SIZE, 3]);
    const result = model.predict(batched);
    const data = await result.data();
    const predictions = {
        sfwScore: data[0],
        racyScore: data[1],
        nsfwScore: data[2]
    }
    console.log(predictions);
}


(async () => inference(url))();

