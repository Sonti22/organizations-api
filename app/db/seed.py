"""Seed database with test data."""

import asyncio
import random
from datetime import datetime

from faker import Faker
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.core.database import AsyncSessionLocal
from app.models import Activity, Building, Organization

fake = Faker("ru_RU")


async def seed_activities(session) -> list[Activity]:
    """Create activity tree (max 3 levels)."""
    print("🌳 Creating activities...")
    
    activities = []
    
    # Level 1 activities
    level1_data = [
        ("Еда", ["Мясная продукция", "Молочная продукция", "Хлебобулочные изделия"]),
        ("Автомобили", ["Грузовые", "Легковые"]),
        ("Строительство", ["Жилые здания", "Коммерческая недвижимость"]),
        ("IT и технологии", ["Разработка ПО", "Консалтинг"]),
    ]
    
    for idx, (level1_name, level2_names) in enumerate(level1_data, start=1):
        # Create level 1
        level1_path = f"{idx:03d}"
        level1 = Activity(
            name=level1_name,
            path=level1_path,
            level=1,
            parent_id=None,
        )
        session.add(level1)
        await session.flush()
        activities.append(level1)
        
        # Create level 2
        for l2_idx, level2_name in enumerate(level2_names, start=1):
            level2_path = f"{level1_path}.{l2_idx:03d}"
            level2 = Activity(
                name=level2_name,
                path=level2_path,
                level=2,
                parent_id=level1.id,
            )
            session.add(level2)
            await session.flush()
            activities.append(level2)
            
            # Create level 3 for some activities
            if random.random() < 0.5:
                level3_names = ["Оптовая торговля", "Розничная торговля", "Производство"]
                for l3_idx, level3_name in enumerate(level3_names[:2], start=1):
                    level3_path = f"{level2_path}.{l3_idx:03d}"
                    level3 = Activity(
                        name=level3_name,
                        path=level3_path,
                        level=3,
                        parent_id=level2.id,
                    )
                    session.add(level3)
                    await session.flush()
                    activities.append(level3)
    
    print(f"✅ Created {len(activities)} activities")
    return activities


async def seed_buildings(session, count: int = 50) -> list[Building]:
    """Create buildings with random locations."""
    print(f"🏗️  Creating {count} buildings...")
    
    buildings = []
    
    # Cities with coordinates
    cities = [
        ("Москва", 55.7558, 37.6173),
        ("Санкт-Петербург", 59.9343, 30.3351),
        ("Новосибирск", 55.0084, 82.9357),
        ("Екатеринбург", 56.8389, 60.6057),
        ("Казань", 55.8304, 49.0661),
    ]
    
    for _ in range(count):
        city_name, base_lat, base_lon = random.choice(cities)
        
        # Add random offset (within ~10km)
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)
        
        # Generate address
        street = fake.street_name()
        building_num = fake.building_number()
        office = random.choice([None, f"офис {random.randint(1, 100)}"])
        
        if office:
            address = f"г. {city_name}, {street}, {building_num}, {office}"
        else:
            address = f"г. {city_name}, {street}, {building_num}"
        
        # Create PostGIS point
        point = Point(lon, lat)
        location_wkb = from_shape(point, srid=4326)
        
        building = Building(
            address=address,
            location=location_wkb,
        )
        session.add(building)
        buildings.append(building)
    
    await session.flush()
    print(f"✅ Created {len(buildings)} buildings")
    return buildings


async def seed_organizations(session, buildings: list[Building], activities: list[Activity], count: int = 100) -> list[Organization]:
    """Create organizations."""
    print(f"🏢 Creating {count} organizations...")
    
    organizations = []
    
    company_types = ["ООО", "АО", "ИП", "ПАО"]
    
    for _ in range(count):
        # Generate name
        company_type = random.choice(company_types)
        company_name = fake.company()
        name = f'{company_type} "{company_name}"'
        
        # Generate phones
        phone_count = random.randint(1, 3)
        phones = []
        for _ in range(phone_count):
            phone = fake.phone_number()
            phones.append(phone)
        
        # Random building
        building = random.choice(buildings)
        
        # Random activities (1-3)
        activity_count = random.randint(1, 3)
        org_activities = random.sample(activities, min(activity_count, len(activities)))
        
        organization = Organization(
            name=name,
            phones=phones,
            building_id=building.id,
            activities=org_activities,
        )
        session.add(organization)
        organizations.append(organization)
    
    await session.flush()
    print(f"✅ Created {len(organizations)} organizations")
    return organizations


async def main():
    """Seed database with test data."""
    print("🌱 Starting database seeding...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if data already exists
            from sqlalchemy import select, func
            
            count_query = select(func.count()).select_from(Organization)
            result = await session.execute(count_query)
            existing_count = result.scalar_one()
            
            if existing_count > 0:
                print(f"⚠️  Database already contains {existing_count} organizations")
                response = input("Do you want to continue? This will add more data. (y/N): ")
                if response.lower() != 'y':
                    print("❌ Seeding cancelled")
                    return
            
            # Seed data
            activities = await seed_activities(session)
            buildings = await seed_buildings(session, count=50)
            organizations = await seed_organizations(session, buildings, activities, count=100)
            
            # Commit
            await session.commit()
            
            print("\n" + "="*50)
            print("✅ Database seeding completed successfully!")
            print("="*50)
            print(f"📊 Summary:")
            print(f"   - Activities: {len(activities)}")
            print(f"   - Buildings: {len(buildings)}")
            print(f"   - Organizations: {len(organizations)}")
            print("\n🚀 You can now start the API server!")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during seeding: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())

