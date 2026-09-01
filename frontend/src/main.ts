import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

// PrimeVue
import PrimeVue from 'primevue/config';
import ToastService from 'primevue/toastservice';
import ConfirmationService from 'primevue/confirmationservice';
import DialogService from 'primevue/dialogservice';

// PrimeVue styles & Icons
import 'primevue/resources/themes/aura-dark-green/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';

// Custom Tailwind & Global styles
import './style.css';

// PrimeVue Component Registrations
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import MultiSelect from 'primevue/multiselect';
import Dialog from 'primevue/dialog';
import Toast from 'primevue/toast';
import ConfirmDialog from 'primevue/confirmdialog';
import Tag from 'primevue/tag';
import Card from 'primevue/card';
import TabView from 'primevue/tabview';
import TabPanel from 'primevue/tabpanel';
import Slider from 'primevue/slider';
import ProgressBar from 'primevue/progressbar';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(PrimeVue, { ripple: true });
app.use(ToastService);
app.use(ConfirmationService);
app.use(DialogService);

// Global PrimeVue Components
app.component('DataTable', DataTable);
app.component('Column', Column);
app.component('Button', Button);
app.component('InputText', InputText);
app.component('InputNumber', InputNumber);
app.component('Dropdown', Dropdown);
app.component('MultiSelect', MultiSelect);
app.component('Dialog', Dialog);
app.component('Toast', Toast);
app.component('ConfirmDialog', ConfirmDialog);
app.component('Tag', Tag);
app.component('Card', Card);
app.component('TabView', TabView);
app.component('TabPanel', TabPanel);
app.component('Slider', Slider);
app.component('ProgressBar', ProgressBar);

app.mount('#app');
