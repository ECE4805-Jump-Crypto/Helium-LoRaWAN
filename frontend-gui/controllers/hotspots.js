const Hotspots = require('../models/Hotspots'); 


// @desc Det all hotspots
// @route GET /api/v1/hotspots
// @access Public
exports.getHotspots = async (req, res, next) => {
    try {
      const hotspots = await Hotspots.find();

      return res.status(200).json({
        success: true,
        count: hotspots.length,
        data: hotspots
      });
    } catch (error) {
      console.error(error);
      res.status(500).json({ error: 'Server error' });
    }
};


// @desc Create a node
// @route POST /api/v1/hotspots
// @access Public
exports.addNodes = async (req, res, next) => {
    try {
      //console.log(req.body);
      const hotspots = await Hotspots.create(req.body);
      
      return res.status(200).json({
        success: true,
        data: hotspots
      });
    } catch (error) {
      console.error(error);
      if(error.code === 11000){
        return res.status(400).json({ error: 'This node already exists' });
      }
      res.status(500).json({ error: 'Server error' });
    }
};