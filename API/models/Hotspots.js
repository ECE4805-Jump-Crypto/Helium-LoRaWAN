const mongoose = require('mongoose');
const geocoder = require('../utils/geocoder');

const HotspotSchema = new mongoose.Schema({
    HotspotsId: {
        type: String,
        required: [true, 'Add a hotspot name'],
        unique: true,
        trim: true,
    },
     address: {
         type: String,
         required: [true, 'Add an address']
     },
    location: {
        type: {
          type: String, // Don't do `{ location: { type: String } }`
          enum: ['Point'], // 'location.type' must be 'Point'
        },
        coordinates: {
          type: [Number],
          index: '2dsphere'
        },
        formattedAddress: String
    },
    gain: {
        type: Number,
        required: [true, 'Add the gain']
    },
    elevation: {
        type: Number,
        required: [true, 'Add the elevation']
    },
    // status: {
    //     type: String,
    //     required: [true, 'Is the hotspots online or offline']
    // },
    createAt: {
        type: Date,
        default: Date.now
    },
    
});

// Geocode & create location
HotspotSchema.pre('save', async function (next) {
    const loc = await geocoder.geocode(this.address);
    
    this.location = {
        type: 'Point',
        coordinates: [loc[0].longitude, loc[0].latitude],
        formattedAddress: loc[0].formattedAddress

    }
    // Do not save address
    this.address = undefined;
    next();
});

module.exports = mongoose.model('Hotspots', HotspotSchema);