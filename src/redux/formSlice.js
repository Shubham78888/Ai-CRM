import { createSlice } from "@reduxjs/toolkit";


const initialState = {
  hcp_name: "",
  interaction_type: "",
  interaction_date: "",
  products_discussed: [],
  discussion_summary: "",
  doctor_feedback: "",
  follow_up_action: "",
  sentiment: ""
};

const formSlice = createSlice({
  name: "form",
  initialState,
  reducers: {
    setFormData: (state, action) => {
      return {
        ...state,
        ...action.payload   // 🔥 merge, not replace
      };
    },
    updateField: (state, action) => {
      const { field, value } = action.payload;
      state[field] = value;
    }
  }
});

export const { setFormData, updateField } = formSlice.actions;
export default formSlice.reducer;