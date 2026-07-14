import { configureStore, createSlice } from '@reduxjs/toolkit';

// Expanded initial state matching the uploaded screenshot fields
const initialFormState = {
  id: null,
  hcpName: '',
  interactionType: 'Meeting',
  date: '2025-04-19',
  time: '19:36',
  attendees: '',
  topicsDiscussed: '',
  materialsShared: [],
  samplesDistributed: [],
  sentiment: 'Neutral',
  outcomes: '',
  followUpActions: '',
  aiSuggestedFollowUps: [
    'Schedule follow-up meeting in 2 weeks',
    'Send OncoBoost Phase III PDF',
    'Add Dr. Sharma to advisory board invite list'
  ],
  highlightedFields: []
};

const formSlice = createSlice({
  name: 'form',
  initialState: initialFormState,
  reducers: {
    updateField: (state, action) => {
      const { field, value } = action.payload;
      state[field] = value;
      if (field !== 'id' && !state.highlightedFields.includes(field)) {
        state.highlightedFields.push(field);
      }
    },
    populateForm: (state, action) => {
      const data = action.payload;
      const changed = [];
      Object.keys(initialFormState).forEach((key) => {
        if (key !== 'highlightedFields' && data[key] !== undefined) {
          if (JSON.stringify(state[key]) !== JSON.stringify(data[key])) {
            state[key] = data[key];
            if (key !== 'id') {
              changed.push(key);
            }
          }
        }
      });
      state.highlightedFields = changed;
    },
    clearForm: (state) => {
      Object.assign(state, initialFormState);
    },
    clearHighlights: (state) => {
      state.highlightedFields = [];
    }
  }
});

// Slice for chat history matching the style in the screenshot
const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        id: 'welcome',
        sender: 'assistant',
        text: 'Log interaction details here (e.g., "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure") or ask for help.',
        timestamp: new Date().toISOString()
      }
    ],
    loading: false
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        ...action.payload
      });
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    }
  }
});

// Slice for interaction logs list
const logsSlice = createSlice({
  name: 'logs',
  initialState: {
    list: []
  },
  reducers: {
    setLogsList: (state, action) => {
      state.list = action.payload;
    },
    addLogToList: (state, action) => {
      state.list.unshift(action.payload);
    }
  }
});

export const { updateField, populateForm, clearForm, clearHighlights } = formSlice.actions;
export const { addMessage, setLoading } = chatSlice.actions;
export const { setLogsList, addLogToList } = logsSlice.actions;

export const store = configureStore({
  reducer: {
    form: formSlice.reducer,
    chat: chatSlice.reducer,
    logs: logsSlice.reducer
  }
});
