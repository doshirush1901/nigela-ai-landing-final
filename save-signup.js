// Local file saving for signups
function saveSignupToFile(email) {
    const timestamp = new Date().toISOString();
    const data = {
        email: email,
        timestamp: timestamp,
        source: 'nigelamasterchef_landing',
        location: 'Mumbai',
        userAgent: navigator.userAgent
    };
    
    // Create CSV content
    const csvLine = `${email},${timestamp},nigelamasterchef_landing,Mumbai,"${navigator.userAgent}"`;
    
    // Download CSV file
    const csvContent = 'Email,Timestamp,Source,Location,UserAgent\n' + csvLine;
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nigela_signup_${timestamp.split('T')[0]}_${timestamp.split('T')[1].split('.')[0].replace(/:/g, '-')}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log('Signup saved to file:', email);
    return data;
}
