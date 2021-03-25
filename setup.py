from setuptools import setup, find_packages

setup(
    name = 'uzu-accounts-app',          
    packages = find_packages(exclude=("Accounts")),  
    version = '2.1.1',      
    license='MIT',        
    description = 'uzu-accounts-app is a generic django application tailored to Single Page Applications that abstracts user authentication and verification from the rest of your project.',
    long_description_content_type = "text/markdown",
    long_description = open("README.md", "r").read(),
    author = 'Collins C. Chinedu (Kolynes)',                   
    author_email = 'collinschinedu@uzucorp.com',      
    url = 'https://github.com/Kolynes/uzu-accounts-app.git',   
    download_url = 'https://github.com/Kolynes/uzu-accounts-app/archive/v1.0.tar.gz',    
    keywords = ['Authentication', 'Django', 'Account Verification'],   
    classifiers=[
        'Development Status :: 3 - Alpha',      
        'Intended Audience :: Developers',      
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',      
        'Programming Language :: Python :: 3.6',
    ],
)