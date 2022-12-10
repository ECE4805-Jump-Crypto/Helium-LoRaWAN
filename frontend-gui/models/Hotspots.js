const mongoose = require('mongoose');
const geocoder = require('../utils/geocoder');

const HotspotSchema = new mongoose.Schema({
    Lat: {
        type: Number,
        require: [true, 'Add the Latitude']
    },
    Lng: {
        type: Number,
        require: [true, 'Add the Longitude']
    },
    gain: {
        type: Number,
        required: [true, 'Add the gain']
    },
    elevation: {
        type: Number,
        required: [true, 'Add the elevation']
    },
    createAt: {
        type: Date,
        default: Date.now
    },
    
});

module.exports = mongoose.model('Hotspots', HotspotSchema);