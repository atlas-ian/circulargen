import React, { useState, useEffect } from 'react';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css';
import 'animate.css/animate.min.css';
import $ from 'jquery';
import 'bootstrap';
import 'bootstrap-datepicker';

function App() {
  // form state
  const [form, setForm] = useState({
    subject: '', agenda: '', audience: '', department: '', urgency: '',
    venue: '', event_datetime: '', additional_info: '', recipient_email: '', date: ''
  });
  const [counters, setCounters] = useState({ info: 0, emails: 0 });
  const [darkMode, setDarkMode] = useState(false);
  const [previewHtml, setPreviewHtml] = useState('');

  // datepicker init
  useEffect(() => {
    $('.datepicker').datepicker({
      format: 'dd-mm-yyyy',
      autoclose: true,
      todayHighlight: true
    }).on('changeDate', e => {
      setForm(f => ({ ...f, date: e.format() }));
    });
  }, []);

  // input handler
  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
    if (name === 'additional_info') setCounters(c => ({ ...c, info: value.length }));
    if (name === 'recipient_email') {
      const list = value.split(',').map(s => s.trim()).filter(s => s);
      setCounters(c => ({ ...c, emails: list.length }));
    }
  };

  // preview
  const handlePreview = () => {
    const html = `
      <h4>${form.subject}</h4>
      <p><strong>Agenda:</strong> ${form.agenda}</p>
      <p><strong>Audience:</strong> ${form.audience}</p>
      <p><strong>Dept:</strong> ${form.department}</p>
      <p><strong>Urgency:</strong> ${form.urgency}</p>
      <p><strong>Date:</strong> ${form.date}</p>
      <hr><p>${form.additional_info}</p>
    `;
    setPreviewHtml(html);
    $('#previewModal').modal('show');
  };

  // submit
  const handleSubmit = e => {
    const arr = form.recipient_email.split(',').map(s => s.trim()).filter(s => s);
    const invalid = arr.filter(s => !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s));
    if (invalid.length) {
      e.preventDefault();
      alert('Invalid email(s):\n' + invalid.join('\n'));
    }
    // else: post to your Django endpoint...
  };

  // toggle theme
  const toggleTheme = () => setDarkMode(dm => !dm);

  return (
    <div className={darkMode ? 'theme-dark' : 'theme-light'}>
      {/* HEADER & NAVBAR */}
      <header className="navbar navbar-expand-lg navbar-light bg-white shadow-sm py-3">
        <a className="navbar-brand font-weight-bold" href="#">
          <img src="/logo.png" alt="Logo" className="mr-2" height="30"/>
          GenCircular
        </a>
        <button className="navbar-toggler" data-toggle="collapse" data-target="#navMenu">
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navMenu">
          <ul className="navbar-nav ml-auto">
            {['Home','About','Contact','Login'].map((link,i) =>
              <li className="nav-item mx-2" key={i}>
                <a className="nav-link" href="#">{link}</a>
              </li>
            )}
            <li className="nav-item ml-3">
              <button className="btn btn-sm btn-outline-secondary" onClick={toggleTheme}>
                {darkMode ? 'Light Mode' : 'Dark Mode'}
              </button>
            </li>
          </ul>
        </div>
      </header>

      {/* MAIN FORM */}
      <main className="container my-5">
        <div className="card shadow-lg animate__animated animate__fadeInUp">
          <div className="card-body p-4">
            <h2 className="card-title mb-4 text-center">Generate Official Circular</h2>
            <form onSubmit={handleSubmit} noValidate>
              {/* render input groups */}
              {[
                {name:'subject', icon:'fas fa-heading', label:'Subject'},
                {name:'agenda', icon:'fas fa-bullseye', label:'Agenda'},
                {name:'audience', icon:'fas fa-users', label:'Target Audience'},
              ].map(f=>
                <div className="form-group floating" key={f.name}>
                  <input
                    type="text" name={f.name} className="form-control"
                    placeholder=" " required value={form[f.name]} onChange={handleChange}
                  />
                  <label><i className={f.icon + ' mr-2'}></i>{f.label}</label>
                </div>
              )}

              {/* selects */}
              {[
                {name:'department', icon:'fas fa-building', label:'Department', options:[
                  'Computer Science and Engineering',
                  'Information Science and Engineering',
                  'Electronics and Communication Engineering',
                  'Mechanical Engineering','Civil Engineering','Electrical and Electronics Engineering'
                ]},
                {name:'urgency', icon:'fas fa-exclamation-circle', label:'Urgency Level', options:['Immediate','Urgent','Medium','Low','Routine']}
              ].map(f=>
                <div className="form-group floating" key={f.name}>
                  <select
                    name={f.name} className="form-control" required
                    value={form[f.name]} onChange={handleChange}
                  >
                    <option value="" disabled hidden/>
                    {f.options.map(o=> <option key={o}>{o}</option>)}
                  </select>
                  <label><i className={f.icon + ' mr-2'}></i>{f.label}</label>
                </div>
              )}

              {/* venue & datetime */}
              {[
                {name:'venue', icon:'fas fa-map-marker-alt', label:'Venue'},
                {name:'event_datetime', icon:'fas fa-calendar-alt', label:'Event Date & Time'}
              ].map(f=>
                <div className="form-group floating" key={f.name}>
                  <input
                    type="text" name={f.name} className="form-control"
                    placeholder=" " required value={form[f.name]} onChange={handleChange}
                  />
                  <label><i className={f.icon + ' mr-2'}></i>{f.label}</label>
                </div>
              )}

              {/* description */}
              <div className="form-group floating">
                <textarea
                  name="additional_info" rows="4" maxLength="400"
                  className="form-control" placeholder=" "
                  value={form.additional_info} onChange={handleChange}
                />
                <label><i className="fas fa-info-circle mr-2"></i>Description</label>
                <small className="form-text text-right">{counters.info} / 400</small>
              </div>

              {/* emails */}
              <div className="form-group floating">
                <input
                  type="text" name="recipient_email" className="form-control"
                  placeholder=" " value={form.recipient_email} onChange={handleChange}
                />
                <label>Recipient Email(s)</label>
                <small className="form-text text-right">
                  {counters.emails} email{counters.emails!==1?'s':''} entered
                </small>
              </div>

              {/* date */}
              <div className="form-group floating">
                <input
                  type="text" name="date" className="form-control datepicker"
                  placeholder=" " required value={form.date} readOnly
                />
                <label><i className="fas fa-calendar-check mr-2"></i>Date of Issue</label>
              </div>

              {/* actions */}
              <div className="text-center">
                <button
                  type="button" className="btn btn-outline-secondary mr-3"
                  onClick={handlePreview}
                >
                  <i className="fas fa-eye"></i> Preview
                </button>
                <button type="submit" className="btn btn-primary">
                  <i className="fas fa-magic"></i> Generate
                </button>
              </div>
            </form>
          </div>
        </div>
      </main>

      {/* PREVIEW MODAL */}
      <div className="modal fade" id="previewModal" tabIndex="-1">
        <div className="modal-dialog modal-lg modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Circular Preview</h5>
              <button type="button" className="close" data-dismiss="modal">&times;</button>
            </div>
            <div className="modal-body" dangerouslySetInnerHTML={{ __html: previewHtml }}/>
            <div className="modal-footer">
              <button type="button" className="btn btn-outline-secondary" data-dismiss="modal">
                Close
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <footer className="bg-white text-center py-3 shadow-sm">
        <small>© {new Date().getFullYear()} Bapuji Institute. All rights reserved.</small>
      </footer>
    </div>
  );
}

export default App;
