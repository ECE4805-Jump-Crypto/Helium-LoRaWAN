const express = require('express');
const { getHotspots, addNodes } = require('../controllers/hotspots');

const router = express.Router();

// router.get('/',(req,res) => {
//     res.send('Hello');
//   }); 


  
router.route('/').get(getHotspots).post(addNodes);

module.exports = router;
