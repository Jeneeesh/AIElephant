import { DataGrid, GridColDef } from '@mui/x-data-grid';
import { Box, Typography } from '@mui/material';

const columns: GridColDef[] = [
  { field: 'id', headerName: 'No', width: 70 },
  { field: 'action', headerName: 'Action', width: 180 },
  { field: 'malayalam', headerName: 'Malayalam', width: 200 },
  { field: 'hindi', headerName: 'Hindi', width: 200 },
  { field: 'gujarati', headerName: 'Gujarati', width: 200 },
  {
    field: 'trigger',
    headerName: 'Repeat',
    width: 120,
    renderCell: (params) => (
      <input 
        type="checkbox"
        onChange={(e) => console.log(`Command ${params.row.id} repeat: ${e.target.checked}`)}
      />
    ),
  },
];

const rows = [
  { 
    id: 1, 
    action: 'Turn Left', 
    malayalam: 'ഇടത്താനെ (Idathāne)', 
    hindi: 'बाएं (Bāẽ)', 
    gujarati: 'ડાબે (Ḍābe)' 
  },
  { 
    id: 2, 
    action: 'Turn Right', 
    malayalam: 'വലത്താനെ (Valathāne)', 
    hindi: 'दाएं (Dāẽ)', 
    gujarati: 'જમણે (Jamaṇe)' 
  },
  { 
    id: 3, 
    action: 'Walk Forward', 
    malayalam: 'നടയാനെ (Naṭayāne)', 
    hindi: 'चल (Chal)', 
    gujarati: 'ચાલ (Chāl)' 
  },
  { 
    id: 4, 
    action: 'Walk Backward', 
    malayalam: 'സെറ്റാനെ (Seṭṭāne)', 
    hindi: 'पीछे (Pīche)', 
    gujarati: 'પાછળ (Pāchaḷ)' 
  },
  { 
    id: 5, 
    action: 'Stop', 
    malayalam: 'നില്ലാനെ (Nillāne)', 
    hindi: 'ठहर (Thahar)', 
    gujarati: 'થોભ (Thobh)' 
  },
  { 
    id: 6, 
    action: 'Lie down', 
    malayalam: 'കിടന്നാനെ (Kiṭannāne)', 
    hindi: 'लेट (Leṭ)', 
    gujarati: 'પડ (Paḍ)' 
  },
  { 
    id: 7, 
    action: 'Sit', 
    malayalam: 'ഇരിയാനെ (Iriyāne)', 
    hindi: 'बैठ (Baiṭh)', 
    gujarati: 'બેસ (Bes)' 
  },
  { 
    id: 8, 
    action: 'Lock foot firmly', 
    malayalam: 'ഊന്നാനെ (Ūnnāne)', 
    hindi: 'जमीन दबा (Jamīn dabā)', 
    gujarati: 'જમીન દબાવ (Jamīn dabāv)' 
  },
  { 
    id: 9, 
    action: 'Lift trunk', 
    malayalam: 'ഭീരിയാനെ (Bhīriyāne)', 
    hindi: 'सूंड उठा (Sūṇḍ uṭhā)', 
    gujarati: 'સુંડ ઊંચી કર (Sūṇḍ ū̃chī kar)' 
  },
  { 
    id: 10, 
    action: 'Bend down for leaves', 
    malayalam: 'എടാനെ (Eṭāne)', 
    hindi: 'झुक कर ले (Jhuk kar le)', 
    gujarati: 'ઝુકીને લે (Jhūkīne le)' 
  },
  { 
    id: 11, 
    action: 'Lift leaves with trunk', 
    malayalam: 'താങ്ങാനെ (Tāṅṅāne)', 
    hindi: 'सूंड से उठा (Sūṇḍ se uṭhā)', 
    gujarati: 'સુંડથી ઊંચક (Sūṇḍthī ū̃chak)' 
  },
  { 
    id: 12, 
    action: 'Give blessing', 
    malayalam: 'ആശീർവദിക്കാനെ (Āśīrvadikkāne)', 
    hindi: 'आशीर्वाद दो (Āśīrvād do)', 
    gujarati: 'આશીર્વાદ આપ (Āśīrvād āp)' 
  },
  { 
    id: 13, 
    action: 'Move ears', 
    malayalam: 'ചെവിയാട്ടാനെ (Cheviyāṭṭāne)', 
    hindi: 'कान हिला (Kān hilā)', 
    gujarati: 'કાન હલાવ (Kān halāv)' 
  },
  { 
    id: 14, 
    action: 'Move head', 
    malayalam: 'തലയാട്ടാനെ (Talayāṭṭāne)', 
    hindi: 'सिर हिला (Sir hilā)', 
    gujarati: 'ડોક હલાવ (Ḍok halāv)' 
  },
  { 
    id: 15, 
    action: 'Lift front leg', 
    malayalam: 'നട പൊക്കാനെ (Naṭa pokkāne)', 
    hindi: 'आगे पैर उठा (Āge pair uṭhā)', 
    gujarati: 'આગળનો પગ ઊંચો કર (Āgaḷno pag ū̄cho kar)' 
  },
  { 
    id: 16, 
    action: 'Lift back leg', 
    malayalam: 'അമരം പൊക്കാനെ (Amaram pokkāne)', 
    hindi: 'पीछे पैर उठा (Pīche pair uṭhā)', 
    gujarati: 'પાછળનો પગ ઊંચો કર (Pāchaḷno pag ū̄cho kar)' 
  },
  { 
    id: 17, 
    action: 'Close eyes', 
    malayalam: 'കണ്ണ് അടയ്ക്കാനെ (Kaṇṇ aṭaykkāne)', 
    hindi: 'आंख बंद (Āṅkh band)', 
    gujarati: 'આંખો બંધ કર (Āṅkho bandh kar)' 
  },
  { 
    id: 18, 
    action: 'Spray water', 
    malayalam: 'ഭീരി ഒഴിയാനെ (Bhīri oḻiyāne)', 
    hindi: 'पानी छिड़क (Pānī chiṛak)', 
    gujarati: 'પાણી છાંટ (Pāṇī chhāṇṭ)' 
  },
  { 
    id: 19, 
    action: 'Stretch legs', 
    malayalam: 'നീട്ടി വെയ്യാനെ (Nīṭṭi veyyāne)', 
    hindi: 'पैर फैला (Pair phailā)', 
    gujarati: 'પગ લંબાવ (Pag lambāv)' 
  },
  { 
    id: 20, 
    action: 'Make sound', 
    malayalam: 'ഒന്നു വിളിച്ചെയാനെ (Onnu viḷiccheyāne)', 
    hindi: 'आवाज कर (Āvāj kar)', 
    gujarati: 'અવાજ કર (Avāj kar)' 
  },
  { 
    id: 21, 
    action: 'Lift leg for climbing', 
    malayalam: 'മടക്കാനെ (Maṭakkāne)', 
    hindi: 'चढ़ने के लिए पैर उठा (Chaṛhne ke lie pair uṭhā)', 
    gujarati: 'ચડવા માટે પગ ઊંચો કર (Chaḍvā māṭe pag ū̄cho kar)' 
  },
  { 
    id: 22, 
    action: 'Stand straight', 
    malayalam: 'നേരെ നില്ലാനെ (Nēre nillāne)', 
    hindi: 'सीधे खड़े हो (Sīdhe khaṛe ho)', 
    gujarati: 'સીધા ઊભા રહે (Sīdhā ū̄bhā rahe)' 
  },
  { 
    id: 23, 
    action: 'Eat', 
    malayalam: 'തിന്നോ ആനെ (Thinnō āne)', 
    hindi: 'खा लो (Khā lo)', 
    gujarati: 'ખા લે (Khā le)' 
  }
];

export default function CommandTable() {
  return (
    <Box sx={{ height: 600, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        checkboxSelection
        disableRowSelectionOnClick
        initialState={{
          pagination: {
            paginationModel: {
              pageSize: 10,
            },
          },
        }}
        pageSizeOptions={[10]}
      />
    </Box>
  );
}