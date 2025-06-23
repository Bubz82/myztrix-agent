import nltk
import os
import ssl

def setup_environment():
    """Download required NLTK data and create necessary directories."""
    print("Setting up environment...")
    
    # Handle SSL certificate issues
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Download required NLTK data
    print("Downloading NLTK data...")
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('wordnet')
        print("NLTK data downloaded successfully!")
    except Exception as e:
        print(f"Error downloading NLTK data: {str(e)}")
        print("Trying alternative download method...")
        try:
            # Try downloading to a specific directory
            nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
            os.makedirs(nltk_data_dir, exist_ok=True)
            nltk.download('punkt', download_dir=nltk_data_dir)
            nltk.download('stopwords', download_dir=nltk_data_dir)
            nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)
            nltk.download('wordnet', download_dir=nltk_data_dir)
            print("NLTK data downloaded successfully to:", nltk_data_dir)
        except Exception as e:
            print(f"Error in alternative download: {str(e)}")
            print("Please try running the following commands manually in Python:")
            print(">>> import nltk")
            print(">>> nltk.download('punkt')")
            print(">>> nltk.download('stopwords')")
            print(">>> nltk.download('averaged_perceptron_tagger')")
            print(">>> nltk.download('wordnet')")
    
    # Create necessary directories
    print("\nCreating directories...")
    os.makedirs('credentials', exist_ok=True)
    
    # Create empty JSON files if they don't exist
    for file in ['pending_events.json', 'declined_events.json']:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write('{}')
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Make sure you have placed your Google OAuth credentials in credentials/client_secrets.json")
    print("2. Run the test script: python test_agent.py")
    print("3. On first run, it will open a browser window for Google authentication")

if __name__ == "__main__":
    setup_environment() 