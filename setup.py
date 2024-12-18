from setuptools import setup, find_packages

setup(
    name='learning_companion',
    version='0.1.0',
    description='An Agentinc Learning Companion grounded on RAG and WebSearchTools',
    author='adkaspar-google',
    author_email='adkaspar@google.com',
    long_description=open('README.MD').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(include=['learning_companion', 'learning_companion.*']),
    install_requires=[
        'langchain>=0.3.12,<0.4.0',
        'tavily-python>=0.5.0,<0.6.0',
        'python-dotenv>=1.0.1,<2.0.0',
        'black>=24.10.0,<25.0.0',
        'isort>=5.13.2,<6.0.0',
        'pytest>=8.3.4,<9.0.0',
        'pypdf>=5.1.0,<6.0.0',
        'beautifulsoup4>=4.12.3,<5.0.0',
        'langgraph>=0.2.59,<0.3.0',
        'langchainhub>=0.1.21,<0.2.0',
        'langchain-community>=0.3.12,<0.4.0',
        'google-api-python-client>=2.155.0,<3.0.0',
        'langchain-google-vertexai>=2.0.9,<3.0.0',
        'langchain-google-genai>=2.0.7,<3.0.0',
        'sphinx>=8.1.3,<9.0.0',
        'build>=1.2.2.post1,<2.0.0',
        'asyncio>=3.4.3,<4.0.0',
        'langchain-chroma>=0.1.4,<0.2.0',
        'langchain-google-community>=2.0.3,<3.0.0',
        'langgraph-checkpoint-sqlite>=2.0.1,<3.0.0'
    ],
    extras_require={
        'test': [
            'pytest>=8.3.4,<9.0.0',
            'requests-mock>=1.12.1,<2.0.0',
        ]
    },
    python_requires='>=3.11',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',  # Assuming MIT License, update if different
        'Operating System :: OS Independent',
    ],
)
