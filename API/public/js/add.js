const nodeForm = document.getElementById('Hotspots-form');
const nodeName = document.getElementById('Hotspots-name');
const nodeAddress = document.getElementById('Hotspots-address');
const nodeGain = document.getElementById('Hotspots-gain');
const nodeElevation = document.getElementById('Hotspots-elevation');


//----------------------------------------------------------
// *****Need Debugging here:
// show all data in totalData
//----------------------------------------------------------
async function addNodes(e){
    e.preventDefault();
    //----------------------------------------------------------
    // *****Need Debugging here:
    // null input won't generate error right now
    // still shows "Node added"
    //----------------------------------------------------------
    if(nodeName.value === ''|| nodeAddress.value ==='' || nodeGain.value ===''||nodeElevation.value===''){
        alert('Please fill in the fields');
    }
    const sendBody = {
        HotspotsId: nodeName.value,
        address: nodeAddress.value,
        gain: nodeGain.value,
        elevation: nodeElevation.value,
    }

    try {
        const res = await fetch('/api/v1/hotspots',{
            method: 'POST',
            headers: {
                'Content-Type':'application/json'
            },
            body: JSON.stringify(sendBody)
        });
        if(res.status === 400){
            throw Error('Nodes already exsts!')

        }
        alert('Node added!');
        window.location.href = '/index.html';
        
    } catch (error) {
        alert(error);
        return;
    }
}



nodeForm.addEventListener('submit', addNodes);