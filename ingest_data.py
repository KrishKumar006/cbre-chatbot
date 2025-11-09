# ingest_data.py - Add sample CBRE data to database
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
except ImportError:
    print("⚠️ Please install requirements: pip install -r requirements.txt")
    print("⚠️ Run: pip install sentence-transformers")
    exit(1)

print("📚 Starting data ingestion...\n")

# Initialize components (FREE local embeddings - no API key needed!)
print("🔄 Loading embedding model (first time may take a minute)...")
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
print("✅ Model loaded!\n")

vectorstore = Chroma(
    collection_name="cbre_docs",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# Sample CBRE commercial real estate data
sample_documents = [
    {
        "content": """CBRE Office Space Solutions
        
CBRE offers comprehensive office space solutions in major metropolitan areas across the United States. Our portfolio includes Class A office buildings featuring modern amenities such as high-speed internet, conference rooms, fitness centers, and 24/7 security. 

We provide flexible lease terms ranging from short-term coworking spaces to long-term corporate headquarters leases. Our office properties are strategically located in prime business districts with excellent access to public transportation, dining, and retail amenities.

Popular locations include New York City (Manhattan), Los Angeles (Downtown and West LA), Chicago (Loop and River North), San Francisco (Financial District), and Austin (Downtown).""",
        "metadata": {"title": "Office Space Solutions", "category": "Office"}
    },
    {
        "content": """Industrial and Warehouse Properties
        
CBRE's industrial and logistics division specializes in warehouse and distribution center properties ranging from 50,000 to over 500,000 square feet. Our facilities feature:

- Clear heights of 28-36 feet
- Multiple dock-high loading doors
- ESFR sprinkler systems
- LED lighting throughout
- Proximity to major highways and interstates
- Rail access available at select locations

These properties are ideal for e-commerce fulfillment, manufacturing, cold storage, and third-party logistics operations. Major industrial markets include the Inland Empire (California), Dallas-Fort Worth, Atlanta, Chicago, and New Jersey.""",
        "metadata": {"title": "Industrial Properties", "category": "Industrial"}
    },
    {
        "content": """2024 Commercial Real Estate Market Trends
        
The commercial real estate market in 2024 shows strong performance in several key areas:

Office Market: Hybrid work models continue to drive demand for flexible, amenity-rich office spaces. Flight to quality remains a dominant trend, with tenants seeking Class A properties with modern technology infrastructure.

Industrial Sector: E-commerce growth fuels continued demand for last-mile distribution facilities. Industrial vacancy rates remain at historic lows in top-tier markets.

Investment Activity: Cap rates have stabilized after the 2023 adjustment period. Institutional investors are actively seeking core assets in primary markets.

Technology Impact: PropTech adoption accelerates, with smart building systems, AI-powered property management, and virtual touring becoming standard offerings.""",
        "metadata": {"title": "2024 Market Trends", "category": "Market Analysis"}
    },
    {
        "content": """CBRE Retail Properties
        
Our retail division manages shopping centers, lifestyle centers, and mixed-use developments across the country. Properties range from neighborhood strip centers to regional malls and premium outlet centers.

Key Features:
- High-traffic locations with excellent visibility
- Co-tenancy with national and regional retailers
- Ample parking with modern amenities
- Common area maintenance programs
- Marketing and promotional support

Retail trends show strong performance for experiential retail, dining, and entertainment concepts. Grocery-anchored centers and medical office adjacencies continue to attract stable traffic.""",
        "metadata": {"title": "Retail Properties", "category": "Retail"}
    },
    {
        "content": """CBRE Leasing Services
        
CBRE provides comprehensive tenant representation and landlord representation services:

Tenant Representation:
- Market analysis and site selection
- Lease negotiation and documentation
- Space planning and design coordination
- Move management services

Landlord Representation:
- Property marketing and positioning
- Tenant prospecting and outreach
- Lease structuring and negotiation
- Portfolio management

Our team of experienced brokers provides market insights, financial analysis, and strategic advice to optimize real estate decisions. We serve clients across all property types and markets nationwide.""",
        "metadata": {"title": "Leasing Services", "category": "Services"}
    },
    {
        "content": """Commercial Real Estate Investment Analysis
        
When evaluating commercial real estate investments, CBRE considers several key metrics:

Cap Rate: Net operating income divided by property value. Current market cap rates range from 4-5% for Class A office to 5-7% for industrial properties.

Cash-on-Cash Return: Annual pre-tax cash flow divided by total cash invested. Target returns typically range from 7-12% depending on asset class and risk profile.

Internal Rate of Return (IRR): Time-weighted return considering all cash flows. Institutional investors typically target 12-18% IRR for value-add strategies.

Occupancy and Tenant Quality: Stable, creditworthy tenants with long-term leases reduce risk and enhance property value.

Location Factors: Proximity to labor pools, transportation infrastructure, and amenities directly impacts property performance and appreciation potential.""",
        "metadata": {"title": "Investment Analysis", "category": "Investment"}
    }
]

print("✍️  Creating documents...")

# Convert to LangChain documents
documents = []
for doc in sample_documents:
    documents.append(
        Document(
            page_content=doc["content"],
            metadata=doc["metadata"]
        )
    )

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)

print("✂️  Splitting into chunks...")
chunks = text_splitter.split_documents(documents)
print(f"   Created {len(chunks)} chunks from {len(documents)} documents")

# Add to vector database
print("📤 Uploading to database...")
vectorstore.add_documents(chunks)

# Persist to disk
vectorstore.persist()

print(f"\n✅ Success! Added {len(chunks)} chunks to database")
print(f"📊 Total documents in database: {vectorstore._collection.count()}")
print("🎉 Data ingestion complete!\n")