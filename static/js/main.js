// Main JavaScript for Youth Club Community

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Password strength indicator (basic)
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            const strength = getPasswordStrength(password);
            updatePasswordStrengthIndicator(strength);
        });
    }
    
    // Initialize month-year picker
    initMonthYearPicker();
    
    // Initialize members carousel
    initMembersCarousel();
    
    // Initialize country dropdowns
    initCountryDropdowns();
    
    // Initialize university dropdowns
    initUniversityDropdowns();
});

function getPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
}

function updatePasswordStrengthIndicator(strength) {
    const indicator = document.getElementById('password-strength');
    if (indicator) {
        const strengthText = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const strengthColors = ['danger', 'warning', 'info', 'success', 'success'];
        
        indicator.textContent = strengthText[strength] || 'Very Weak';
        indicator.className = `badge bg-${strengthColors[strength] || 'danger'}`;
    }
}

// Month-Year Picker functionality
function initMonthYearPicker() {
    const startDateInput = document.getElementById('start_date');
    const endDateInput = document.getElementById('end_date');
    
    // Create the picker modals
    const startPickerModal = createMonthYearPickerModal('start');
    const endPickerModal = createMonthYearPickerModal('end');
    document.body.appendChild(startPickerModal);
    document.body.appendChild(endPickerModal);
    
    // Setup start date picker
    if (startDateInput) {
        startDateInput.addEventListener('click', function(e) {
            e.preventDefault();
            showMonthYearPicker('start');
        });
        startDateInput.addEventListener('keydown', function(e) {
            e.preventDefault();
        });
    }
    
    // Setup end date picker
    if (endDateInput) {
        endDateInput.addEventListener('click', function(e) {
            e.preventDefault();
            showMonthYearPicker('end');
        });
        endDateInput.addEventListener('keydown', function(e) {
            e.preventDefault();
        });
    }
}

function createMonthYearPickerModal(type) {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = `monthYearPickerModal_${type}`;
    modal.innerHTML = `
        <div class="modal-dialog modal-sm">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Select Month & Year</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="row">
                        <div class="col-6">
                            <label class="form-label">Month</label>
                            <select class="form-select" id="monthSelect_${type}">
                                <option value="01">January</option>
                                <option value="02">February</option>
                                <option value="03">March</option>
                                <option value="04">April</option>
                                <option value="05">May</option>
                                <option value="06">June</option>
                                <option value="07">July</option>
                                <option value="08">August</option>
                                <option value="09">September</option>
                                <option value="10">October</option>
                                <option value="11">November</option>
                                <option value="12">December</option>
                            </select>
                        </div>
                        <div class="col-6">
                            <label class="form-label">Year</label>
                            <select class="form-select" id="yearSelect_${type}">
                                ${generateYearOptions()}
                            </select>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="confirmDate_${type}">Select</button>
                </div>
            </div>
        </div>
    `;
    return modal;
}

function generateYearOptions() {
    const currentYear = new Date().getFullYear();
    const maxYear = currentYear + 10; // Allow up to 10 years in the future
    let options = '';
    for (let year = maxYear; year >= 1990; year--) {
        options += `<option value="${year}">${year}</option>`;
    }
    return options;
}

function showMonthYearPicker(type) {
    const modal = new bootstrap.Modal(document.getElementById(`monthYearPickerModal_${type}`));
    
    // Set default values based on type
    const currentYear = new Date().getFullYear();
    const monthSelect = document.getElementById(`monthSelect_${type}`);
    const yearSelect = document.getElementById(`yearSelect_${type}`);
    
    if (type === 'start') {
        // For start date, default to current year
        yearSelect.value = currentYear;
        monthSelect.value = '09'; // September (typical start of academic year)
    } else {
        // For end date, default to 4 years from now (typical graduation time)
        yearSelect.value = currentYear + 4;
        monthSelect.value = '06'; // June (typical graduation month)
    }
    
    modal.show();
    
    // Set up confirm button
    document.getElementById(`confirmDate_${type}`).addEventListener('click', function() {
        const month = monthSelect.value;
        const year = yearSelect.value;
        const formattedDate = `${month}-${year}`;
        
        const targetInput = type === 'start' ? 'start_date' : 'end_date';
        document.getElementById(targetInput).value = formattedDate;
        modal.hide();
    });
}

// Members Carousel functionality
function initMembersCarousel() {
    const carouselTrack = document.getElementById('carouselTrack');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const indicatorsContainer = document.getElementById('carouselIndicators');
    
    if (!carouselTrack || !prevBtn || !nextBtn) return;
    
    let currentIndex = 0;
    let autoScrollInterval;
    let isAutoScrolling = true;
    
    // Get member cards from the DOM (already rendered by server)
    const memberCards = carouselTrack.querySelectorAll('.member-card-carousel');
    const memberCount = memberCards.length / 2; // Divide by 2 because we duplicate for seamless loop
    
    // Create member cards (this function is now simplified since cards are server-rendered)
    function createMemberCards() {
        // Cards are already created by the server, just ensure proper setup
        if (memberCards.length === 0) return;
    }
    
    // Create indicators
    function createIndicators() {
        indicatorsContainer.innerHTML = '';
        for (let i = 0; i < memberCount; i++) {
            const indicator = document.createElement('button');
            indicator.className = `carousel-indicator ${i === 0 ? 'active' : ''}`;
            indicator.addEventListener('click', () => goToSlide(i));
            indicatorsContainer.appendChild(indicator);
        }
    }
    
    // Update indicators
    function updateIndicators(index) {
        const indicators = indicatorsContainer.querySelectorAll('.carousel-indicator');
        indicators.forEach((indicator, i) => {
            indicator.classList.toggle('active', i === index);
        });
    }
    
    // Go to specific slide
    function goToSlide(index) {
        currentIndex = index;
        const cardWidth = 280 + 24; // card width + gap
        const translateX = -currentIndex * cardWidth;
        carouselTrack.style.transform = `translateX(${translateX}px)`;
        updateIndicators(currentIndex);
        
        // Reset auto-scroll
        if (isAutoScrolling) {
            clearInterval(autoScrollInterval);
            startAutoScroll();
        }
    }
    
    // Next slide
    function nextSlide() {
        currentIndex = (currentIndex + 1) % memberCount;
        goToSlide(currentIndex);
    }
    
    // Previous slide
    function prevSlide() {
        currentIndex = (currentIndex - 1 + memberCount) % memberCount;
        goToSlide(currentIndex);
    }
    
    // Start auto-scroll
    function startAutoScroll() {
        if (isAutoScrolling) {
            autoScrollInterval = setInterval(nextSlide, 3000); // Change slide every 3 seconds
        }
    }
    
    // Stop auto-scroll
    function stopAutoScroll() {
        clearInterval(autoScrollInterval);
    }
    
    // Event listeners
    nextBtn.addEventListener('click', () => {
        stopAutoScroll();
        nextSlide();
        isAutoScrolling = false;
    });
    
    prevBtn.addEventListener('click', () => {
        stopAutoScroll();
        prevSlide();
        isAutoScrolling = false;
    });
    
    // Pause auto-scroll on hover
    carouselTrack.addEventListener('mouseenter', stopAutoScroll);
    carouselTrack.addEventListener('mouseleave', () => {
        isAutoScrolling = true;
        startAutoScroll();
    });
    
    // Touch/swipe support for mobile
    let startX = 0;
    let isDragging = false;
    
    carouselTrack.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        isDragging = true;
        stopAutoScroll();
    });
    
    carouselTrack.addEventListener('touchmove', (e) => {
        if (!isDragging) return;
        e.preventDefault();
    });
    
    carouselTrack.addEventListener('touchend', (e) => {
        if (!isDragging) return;
        
        const endX = e.changedTouches[0].clientX;
        const diff = startX - endX;
        
        if (Math.abs(diff) > 50) { // Minimum swipe distance
            if (diff > 0) {
                nextSlide();
            } else {
                prevSlide();
            }
        }
        
        isDragging = false;
        isAutoScrolling = true;
        startAutoScroll();
    });
    
    // Initialize carousel
    createMemberCards();
    createIndicators();
    startAutoScroll();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        goToSlide(currentIndex);
    });
}

// Country Dropdown functionality
function initCountryDropdowns() {
    const countryDropdowns = document.querySelectorAll('.country-dropdown');
    
    countryDropdowns.forEach(dropdown => {
        const input = dropdown.querySelector('.country-input');
        const list = dropdown.querySelector('.country-dropdown-list');
        const arrow = dropdown.querySelector('.country-dropdown-arrow');
        
        if (!input || !list) return;
        
        let isOpen = false;
        let highlightedIndex = -1;
        let filteredCountries = [];
        
        // Country list
        const countries = [
            'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria',
            'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
            'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia',
            'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica',
            'Croatia', 'Cuba', 'Cyprus', 'Czech Republic', 'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador',
            'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France',
            'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau',
            'Guyana', 'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland',
            'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan',
            'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar',
            'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia',
            'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal',
            'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan',
            'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar',
            'Romania', 'Russia', 'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia',
            'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa',
            'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan',
            'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan',
            'Tuvalu', 'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City',
            'Venezuela', 'Vietnam', 'Yemen', 'Zambia', 'Zimbabwe'
        ];
        
        // Populate dropdown with all countries initially
        function populateDropdown(countriesToShow = countries) {
            list.innerHTML = '';
            filteredCountries = countriesToShow;
            
            countriesToShow.forEach((country, index) => {
                const option = document.createElement('div');
                option.className = 'country-option';
                option.textContent = country;
                option.addEventListener('click', () => selectCountry(country));
                list.appendChild(option);
            });
        }
        
        // Select a country
        function selectCountry(country) {
            input.value = country;
            closeDropdown();
        }
        
        // Open dropdown
        function openDropdown() {
            isOpen = true;
            dropdown.classList.add('open');
            list.classList.add('show');
            populateDropdown();
        }
        
        // Close dropdown
        function closeDropdown() {
            isOpen = false;
            dropdown.classList.remove('open');
            list.classList.remove('show');
            highlightedIndex = -1;
        }
        
        // Filter countries based on input
        function filterCountries(query) {
            const filtered = countries.filter(country => 
                country.toLowerCase().includes(query.toLowerCase())
            );
            populateDropdown(filtered);
        }
        
        // Highlight option
        function highlightOption(index) {
            const options = list.querySelectorAll('.country-option');
            options.forEach((option, i) => {
                option.classList.toggle('highlighted', i === index);
            });
        }
        
        // Event listeners
        input.addEventListener('focus', openDropdown);
        input.addEventListener('click', openDropdown);
        input.addEventListener('input', (e) => {
            const query = e.target.value;
            if (query.length > 0) {
                filterCountries(query);
            } else {
                populateDropdown();
            }
            highlightedIndex = -1;
        });
        
        input.addEventListener('keydown', (e) => {
            if (!isOpen) return;
            
            const options = list.querySelectorAll('.country-option');
            
            switch(e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    highlightedIndex = Math.min(highlightedIndex + 1, options.length - 1);
                    highlightOption(highlightedIndex);
                    options[highlightedIndex]?.scrollIntoView({ block: 'nearest' });
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    highlightedIndex = Math.max(highlightedIndex - 1, 0);
                    highlightOption(highlightedIndex);
                    options[highlightedIndex]?.scrollIntoView({ block: 'nearest' });
                    break;
                case 'Enter':
                    e.preventDefault();
                    if (highlightedIndex >= 0 && options[highlightedIndex]) {
                        selectCountry(options[highlightedIndex].textContent);
                    }
                    break;
                case 'Escape':
                    closeDropdown();
                    break;
            }
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!dropdown.contains(e.target)) {
                closeDropdown();
            }
        });
        
        // Initialize with all countries
        populateDropdown();
    });
}

// University Dropdown functionality
function initUniversityDropdowns() {
    const universityDropdown = document.querySelector('.university-dropdown');
    const countryInput = document.querySelector('#university_country');
    
    if (!universityDropdown || !countryInput) return;
    
    const input = universityDropdown.querySelector('.university-input');
    const list = universityDropdown.querySelector('.university-dropdown-list');
    const arrow = universityDropdown.querySelector('.university-dropdown-arrow');
    
    if (!input || !list) return;
    
    let isOpen = false;
    let highlightedIndex = -1;
    let universities = [];
    let currentCountry = '';
    let isLoading = false;
    
    // University API base URL
    const API_BASE_URL = 'http://universities.hipolabs.com/search';
    
    // Fallback university data for common countries
    const FALLBACK_UNIVERSITIES = {
        'United States': [
            'Harvard University', 'Stanford University', 'Massachusetts Institute of Technology',
            'University of California, Berkeley', 'Yale University', 'Princeton University',
            'Columbia University', 'University of Chicago', 'California Institute of Technology',
            'University of Pennsylvania', 'Johns Hopkins University', 'Northwestern University',
            'Duke University', 'Dartmouth College', 'Brown University', 'Cornell University',
            'Rice University', 'Vanderbilt University', 'Washington University in St. Louis',
            'Emory University', 'Georgetown University', 'Carnegie Mellon University',
            'University of California, Los Angeles', 'University of Michigan', 'University of Virginia',
            'University of North Carolina at Chapel Hill', 'New York University', 'University of Southern California',
            'University of Texas at Austin', 'Boston University', 'Tulane University',
            'University of Wisconsin-Madison', 'University of Illinois at Urbana-Champaign',
            'Ohio State University', 'Pennsylvania State University', 'University of Florida',
            'University of Georgia', 'University of Washington', 'University of Oregon',
            'Arizona State University', 'University of Arizona', 'University of Colorado Boulder'
        ],
        'United Kingdom': [
            'University of Oxford', 'University of Cambridge', 'Imperial College London',
            'London School of Economics and Political Science', 'University College London',
            'University of Edinburgh', 'King\'s College London', 'University of Manchester',
            'University of Bristol', 'University of Warwick', 'University of Glasgow',
            'University of Birmingham', 'University of Sheffield', 'University of Leeds',
            'University of Liverpool', 'University of Nottingham', 'University of Southampton',
            'University of York', 'University of Durham', 'University of Exeter',
            'University of Bath', 'University of Sussex', 'University of Lancaster',
            'University of Leicester', 'University of Reading', 'University of Surrey',
            'University of East Anglia', 'University of Kent', 'University of Essex',
            'University of Hull', 'University of Bradford', 'University of Salford'
        ],
        'Canada': [
            'University of Toronto', 'University of British Columbia', 'McGill University',
            'University of Alberta', 'McMaster University', 'University of Waterloo',
            'Western University', 'Queen\'s University', 'University of Calgary',
            'Simon Fraser University', 'University of Ottawa', 'University of Montreal',
            'University of Manitoba', 'Dalhousie University', 'University of Saskatchewan',
            'Carleton University', 'University of Victoria', 'Concordia University',
            'York University', 'University of Guelph', 'Memorial University of Newfoundland',
            'University of New Brunswick', 'Brock University', 'Trent University',
            'University of Windsor', 'Ryerson University', 'University of Regina'
        ],
        'Germany': [
            'Technical University of Munich', 'Ludwig Maximilian University of Munich',
            'Heidelberg University', 'Karlsruhe Institute of Technology', 'Humboldt University of Berlin',
            'Free University of Berlin', 'RWTH Aachen University', 'University of Stuttgart',
            'University of Hamburg', 'University of Cologne', 'University of Frankfurt',
            'University of Bonn', 'University of Göttingen', 'University of Tübingen',
            'University of Freiburg', 'University of Würzburg', 'University of Münster',
            'University of Erlangen-Nuremberg', 'University of Kiel', 'University of Mainz'
        ],
        'France': [
            'Sorbonne University', 'École Polytechnique', 'École Normale Supérieure',
            'University of Paris-Saclay', 'Sciences Po', 'HEC Paris',
            'École des Ponts ParisTech', 'University of Lyon', 'University of Strasbourg',
            'University of Aix-Marseille', 'University of Toulouse', 'University of Lille',
            'University of Bordeaux', 'University of Montpellier', 'University of Rennes',
            'University of Nantes', 'University of Grenoble', 'University of Nancy'
        ],
        'Australia': [
            'University of Melbourne', 'University of Sydney', 'Australian National University',
            'University of Queensland', 'Monash University', 'University of New South Wales',
            'University of Western Australia', 'University of Adelaide', 'University of Technology Sydney',
            'Queensland University of Technology', 'Macquarie University', 'Griffith University',
            'Deakin University', 'University of Wollongong', 'Curtin University',
            'University of South Australia', 'La Trobe University', 'Flinders University'
        ],
        'Japan': [
            'University of Tokyo', 'Kyoto University', 'Osaka University',
            'Tohoku University', 'Nagoya University', 'Kyushu University',
            'Hokkaido University', 'Tokyo Institute of Technology', 'Waseda University',
            'Keio University', 'Hitotsubashi University', 'Tokyo Medical and Dental University',
            'Chiba University', 'Kanazawa University', 'Okayama University'
        ],
        'China': [
            'Tsinghua University', 'Peking University', 'Fudan University',
            'Shanghai Jiao Tong University', 'Zhejiang University', 'University of Science and Technology of China',
            'Nanjing University', 'Sun Yat-sen University', 'Huazhong University of Science and Technology',
            'Xi\'an Jiaotong University', 'Harbin Institute of Technology', 'Tongji University',
            'Beijing Normal University', 'Tianjin University', 'Southeast University'
        ],
        'India': [
            'Indian Institute of Technology Bombay', 'Indian Institute of Technology Delhi',
            'Indian Institute of Technology Madras', 'Indian Institute of Science',
            'Indian Institute of Technology Kanpur', 'Indian Institute of Technology Kharagpur',
            'University of Delhi', 'Jawaharlal Nehru University', 'University of Mumbai',
            'University of Calcutta', 'Banaras Hindu University', 'Aligarh Muslim University',
            'University of Pune', 'Anna University', 'Jadavpur University'
        ],
        'Brazil': [
            'University of São Paulo', 'State University of Campinas', 'Federal University of Rio de Janeiro',
            'Federal University of Minas Gerais', 'University of Brasília', 'Federal University of São Paulo',
            'Pontifical Catholic University of Rio de Janeiro', 'Federal University of Rio Grande do Sul',
            'University of São Paulo', 'Federal University of Bahia', 'Federal University of Paraná'
        ]
    };
    
    // Fetch universities by country
    async function fetchUniversities(country) {
        if (!country || country === currentCountry) return universities;
    
        isLoading = true;
        showLoading();
    
        try {
            // Try to fetch from API first
            const response = await fetch(`${API_BASE_URL}?country=${encodeURIComponent(country)}`, {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Accept': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                universities = data.map(uni => ({
                    name: uni.name,
                    country: uni.country,
                    domains: uni.domains || [],
                    web_pages: uni.web_pages || []
                }));
                currentCountry = country;
            } else {
                throw new Error('API request failed');
            }
        } catch (error) {
            console.log('API failed, using fallback data:', error.message);
            
            // Fallback to local data
            const fallbackList = FALLBACK_UNIVERSITIES[country] || [];
            if (fallbackList.length > 0) {
                universities = fallbackList.map(name => ({
                    name: name,
                    country: country,
                    domains: [],
                    web_pages: []
                }));
                currentCountry = country;
            } else {
                universities = []; // No universities for this country
            }
        }
    
        isLoading = false;
        
        if (universities.length === 0) {
            showError(`No universities found for ${country}. Please type to search manually.`);
        } else {
            showNoResults(); // This will show the universities
        }
        
        return universities;
    }
    
    // Show loading state
    function showLoading() {
        list.innerHTML = '<div class="university-loading">Loading universities...</div>';
    }
    
    // Show error state
    function showError(message) {
        list.innerHTML = `<div class="university-no-results">${message}</div>`;
    }
    
    // Show no results
    function showNoResults() {
        if (universities.length > 0) {
            // Show the fallback universities
            populateDropdown(universities);
        } else {
            list.innerHTML = '<div class="university-no-results">No universities found. Try typing to search.</div>';
        }
    }
    
    // Populate dropdown with universities
    function populateDropdown(universitiesToShow = universities) {
        list.innerHTML = '';
        
        if (universitiesToShow.length === 0) {
            showNoResults();
            return;
        }
        
        universitiesToShow.forEach((university, index) => {
            const option = document.createElement('div');
            option.className = 'university-option';
            option.innerHTML = `
                <div class="fw-bold">${university.name}</div>
                ${university.domains.length > 0 ? `<small class="text-muted">${university.domains[0]}</small>` : ''}
            `;
            option.addEventListener('click', () => selectUniversity(university.name));
            list.appendChild(option);
        });
    }
    
    // Select a university
    function selectUniversity(universityName) {
        input.value = universityName;
        closeDropdown();
    }
    
    // Open dropdown
    function openDropdown() {
        if (isLoading) return;
        
        isOpen = true;
        universityDropdown.classList.add('open');
        list.classList.add('show');
        
        if (universities.length === 0 && currentCountry) {
            populateDropdown();
        }
    }
    
    // Close dropdown
    function closeDropdown() {
        isOpen = false;
        universityDropdown.classList.remove('open');
        list.classList.remove('show');
        highlightedIndex = -1;
    }
    
    // Filter universities based on input
    function filterUniversities(query) {
        if (query.length === 0) {
            populateDropdown();
            return;
        }
        
        const filtered = universities.filter(uni => 
            uni.name.toLowerCase().includes(query.toLowerCase()) ||
            (uni.domains.length > 0 && uni.domains.some(domain => 
                domain.toLowerCase().includes(query.toLowerCase())
            ))
        );
        
        if (filtered.length === 0 && query.length > 2) {
            // If no matches found and user has typed enough, show option to add custom university
            list.innerHTML = `
                <div class="university-option" onclick="selectUniversity('${query}')">
                    <div class="fw-bold">Add "${query}" as university</div>
                    <small class="text-muted">Click to select this university</small>
                </div>
            `;
        } else {
            populateDropdown(filtered);
        }
    }
    
    // Highlight option
    function highlightOption(index) {
        const options = list.querySelectorAll('.university-option');
        options.forEach((option, i) => {
            option.classList.toggle('highlighted', i === index);
        });
    }
    
    // Event listeners
    input.addEventListener('focus', openDropdown);
    input.addEventListener('click', openDropdown);
    input.addEventListener('input', (e) => {
        const query = e.target.value;
        if (query.length > 0) {
            filterUniversities(query);
        } else {
            populateDropdown();
        }
        highlightedIndex = -1;
    });
    
    input.addEventListener('keydown', (e) => {
        if (!isOpen) return;
        
        const options = list.querySelectorAll('.university-option');
        
        switch(e.key) {
            case 'ArrowDown':
                e.preventDefault();
                highlightedIndex = Math.min(highlightedIndex + 1, options.length - 1);
                highlightOption(highlightedIndex);
                options[highlightedIndex]?.scrollIntoView({ block: 'nearest' });
                break;
            case 'ArrowUp':
                e.preventDefault();
                highlightedIndex = Math.max(highlightedIndex - 1, 0);
                highlightOption(highlightedIndex);
                options[highlightedIndex]?.scrollIntoView({ block: 'nearest' });
                break;
            case 'Enter':
                e.preventDefault();
                if (highlightedIndex >= 0 && options[highlightedIndex]) {
                    const universityName = options[highlightedIndex].querySelector('.fw-bold').textContent;
                    selectUniversity(universityName);
                }
                break;
            case 'Escape':
                closeDropdown();
                break;
        }
    });
    
    // Watch for country changes
    countryInput.addEventListener('input', async (e) => {
        const country = e.target.value;
        if (country && country !== currentCountry) {
            universities = await fetchUniversities(country);
            if (isOpen) {
                populateDropdown();
            }
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!universityDropdown.contains(e.target)) {
            closeDropdown();
        }
    });
    
    // Initialize with empty state
    list.innerHTML = '<div class="university-no-results">Select a country to see universities</div>';
}
