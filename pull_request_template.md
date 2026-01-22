## Summary

Implements the Cars feature following Domain-Driven Design (DDD) and Clean Architecture principles. Includes domain entity with validation, repository pattern, use cases, Django models, and complete API endpoints following the OpenAPI contract.

## How to Test

1. Create a new car: `POST /cars` with required fields (name, brand, model, year, plate_number, color, price_per_day, regional)
2. List all cars: `GET /cars`
3. List cars by region: `GET /cars?r=1&s=1737792000&e=1738224000`
4. Get specific car: `GET /cars/{id}`
5. Update car: `PUT /cars/{id}` with partial fields
6. Delete car: `DELETE /cars/{id}`
7. Expected result: All endpoints return proper HTTP status codes and follow OpenAPI schema

## Related Issues

<!-- Link to relevant issues, e.g., Closes #123 -->

## Author Checklist

- [x] Code follows team coding standards and style guide
- [x] Self-reviewed the code changes
- [ ] Added/updated tests for new functionality
- [ ] All tests pass locally
- [x] Code is properly documented
- [ ] Synced with latest `develop` branch
- [x] PR title follows conventional commit format
- [x] Meaningful commit messages used

## Additional Notes

**Changes by Layer:**

**Domain Layer** (`src/domain/`)
- Car entity with validation (name, brand, model, year, plate_number, color, price_per_day, regional_id)
- CarRepository abstract interface with contracts

**Application Layer** (`src/application/`)
- CreateCarUseCase, GetCarByIdUseCase, GetCarsUseCase, UpdateCarUseCase, DeleteCarUseCase

**Infrastructure Layer** (`src/infrastructure/`)
- CarModel Django model with database indexes
- DjangoCarRepository implementation with ORM and error handling

**API Layer** (`src/api/`)
- Car DTOs/Schemas with field validators
- Complete Car API endpoints (CREATE, READ, UPDATE, DELETE, LIST)

All endpoints match the OpenAPI specification defined in `api/openapi.yml`.

## Type of task

- [ ] Data Processing
- [ ] Model Training
- [x] API Development
- [ ] UI Development
- [ ] Testing
- [ ] Debugging
- [ ] Refactor
- [ ] Performance Improvement / Optimization
- [ ] Security
- [ ] Documentation
- [ ] Monitoring

## Reviewer(s)

<!-- Please add the names or GitHub usernames of the reviewers -->

- [ ] @reviewer1
- [ ] @reviewer2
