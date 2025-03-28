import random
from collections import defaultdict


class Atom:
    id = defaultdict(int)

    def __init__(self, predicate, id=None):
        self.predicate = predicate
        self.value = id
        if id is None:
            self.value = Atom.id[predicate]
            Atom.id[predicate] += 1

    def __str__(self):
        return f'{self.predicate}({self.value}).'


class Relation:
    def __init__(self, predicate, atom1, atom2):
        self.predicate = predicate
        self.atom1 = atom1
        self.atom2 = atom2

    def __str__(self):
        return f'{self.predicate}({str(self.atom1).removesuffix(".")},{str(self.atom2).removesuffix(".")}).'


class Pool:
    def __init__(self):
        self.pool = defaultdict(list)

    def generate(self, predicate):
        res = Atom(predicate)
        self.pool[predicate].append(res)
        return res

    def get(self, predicate, id):
        if isinstance(id, int):
            while Atom.id[predicate] < id:
                self.generate(predicate)
        return Atom(predicate, id)


class Current:
    def __init__(self, pool):
        self.pool = pool
        self.current = {}

    def get(self, predicate):
        if predicate not in self.current:
            self.current[predicate] = self.pool.generate(predicate)
        return self.current[predicate]


def generate_branch(pool: Pool):
    res = []
    for _ in range(N_BRANCH):
        res.append(pool.generate('return_branch'))
    return res


def generate_rental_rules(pool: Pool, current):
    res = []
    rental = current.get('rental')
    rental_period = current.get('rental_period')
    return_branch = pool.get('return_branch', random.randint(0, N_BRANCH))
    requested_car_group = current.get('requested_car_group')
    advance_rental = current.get('advance_rental_date_time')
    booking_date = current.get('booking_date_time')
    scheduled_pick_up = pool.get('scheduled_pick_up_date_time', booking_date.value + 1)
    rental_booking = current.get('rental_booking')
    res.extend([rental, rental_period, return_branch, requested_car_group,
                scheduled_pick_up, advance_rental, booking_date, rental_booking])
    res.extend([
        Relation('has', rental, requested_car_group),
        Relation('includes', rental, rental_period),
        Relation('has', rental, return_branch),
        Relation('has', advance_rental, scheduled_pick_up),
        Relation('has', advance_rental, booking_date),
        Relation('establishes', rental_booking, advance_rental)
    ])
    return res


def generate_payment_rules(pool: Pool, current):
    res = []
    rental = current.get('rental')
    open = pool.get('open', rental.value)
    estimated_rental_charge = current.get('estimated_rental_charge')
    credit_card = current.get('credit_card')
    renter = current.get('renter')
    res.extend([rental, open, estimated_rental_charge, credit_card, renter])
    res.extend([
        Relation('has', renter, credit_card),
        Relation('is_responsible_of', renter, rental),
        Relation('is_provisionally_charged_to', estimated_rental_charge, credit_card),
    ])
    rental_charge = current.get('rental_charge')
    business_currency = current.get('business_currency')
    res.extend([rental_charge, business_currency])
    res.extend([
        Relation('is_calculated_in', rental_charge, business_currency),
        Relation('has', rental, rental_charge),
        Relation('has', rental, business_currency),
    ])
    price_conversion = current.get('price_conversion')
    currency = current.get('currency')
    res.extend([price_conversion, currency])
    res.extend([
        Relation('has', rental, renter),
        Relation('requests', renter, price_conversion),
        Relation('is_converted_to', rental_charge, currency),
        Relation('has', price_conversion, currency),
    ])
    cash_rental = current.get('cash_rental')
    lowest_rental_price = current.get('lowest_rental_price')
    res.extend([cash_rental, lowest_rental_price])
    res.extend([
        Relation('honors', cash_rental, lowest_rental_price),
    ])
    return res


def generate_diver_rules(pool: Pool, current):
    res = []
    rental = current.get('rental')
    driver = current.get('driver')
    qualified = pool.get('qualified', driver.value)
    res.extend([rental, driver, qualified])
    res.extend([
        Relation('has', rental, driver),
    ])
    return res


def generate_return_rules(pool: Pool, current):
    res = []
    country = current.get('country')
    return_branch = current.get('return_branch')
    international_inward_rental = current.get('international_inward_rental')
    rented_car = current.get('rented_car')
    country_of_registration = current.get('country_of_registration')
    res.extend([country, return_branch, country_of_registration,
                international_inward_rental, rented_car])
    res.extend([
        Relation('has', return_branch, country),
        Relation('has', international_inward_rental, return_branch),
        Relation('has', international_inward_rental, rented_car),
        Relation('has', rented_car, country_of_registration),
    ])
    in_country_rental = current.get('in_country_rental')
    actual_return_date_time = current.get('actual_return_date_time')
    local_area = current.get('local_area')
    res.extend([in_country_rental, actual_return_date_time, local_area])
    res.extend([
        Relation('has', in_country_rental, actual_return_date_time),
        Relation('owns', local_area, rented_car),
        Relation('has', in_country_rental, return_branch),
        Relation('is_included_in', return_branch, local_area),
        Relation('has', in_country_rental, rented_car),
    ])
    rental = current.get('rental')
    open = pool.get('open', rental.value)
    pick_up_branch = pool.get('pick_up_branch', random.randint(0, N_BRANCH))
    res.extend([rental, open, pick_up_branch])
    res.extend([
        Relation('is_owned_by', rented_car, local_area),
        Relation('has', international_inward_rental, rented_car),
        Relation('has', international_inward_rental, pick_up_branch),
        Relation('is_included_in', pick_up_branch, local_area),
    ])
    end_date_time = pool.get('end_date_time', actual_return_date_time.value - 1)
    grace_period = current.get('grace_period')
    late_return_charge = current.get('late_return_charge')
    res.extend([end_date_time, grace_period, late_return_charge])
    res.extend([
        Relation('has', rental, actual_return_date_time),
        Relation('has', rental, grace_period),
        Relation('has', grace_period, end_date_time),
        Relation('incurs', rental, late_return_charge),
    ])
    drop_off_location = pool.get('drop_off_location', random.randint(0, N_BRANCH))
    eu_rent_site = current.get('eu_rent_site')
    location_penalty_charge = current.get('location_penalty_charge')
    res.extend([drop_off_location, eu_rent_site, location_penalty_charge])
    res.extend([
        Relation('has', rental, drop_off_location),
        Relation('incurs', rental, location_penalty_charge),
        Relation('is_base_for', eu_rent_site, return_branch),
    ])
    assigned = pool.get('assigned', rental.value)
    res.extend([assigned])
    res.extend([
        Relation('is_stored_at', rental, pick_up_branch),
        Relation('has', rental, rented_car),
        Relation('incurs', rental, pick_up_branch),
    ])
    actual_start_date_time = current.get('actual_start_date_time')
    fuel_level = pool.get('fuel_level', 'full')
    res.extend([actual_start_date_time, fuel_level])
    res.extend([
        Relation('has', rental, actual_start_date_time),
        Relation('has', rental, rented_car),
        Relation('has', rented_car, fuel_level),
    ])
    return res


def generate_rental_period(pool: Pool, current):
    res = []
    start_date = current.get('start_date')
    reserved_rental = current.get('reserved_rental')
    res.extend([start_date, reserved_rental])
    res.extend([
        Relation('has', reserved_rental, start_date),
    ])
    rental_duration = pool.get('rental_duration', random.randint(0, 90))
    rental = current.get('rental')
    res.extend([rental_duration, rental])
    res.extend([
        Relation('has', rental, rental_duration),
    ])
    return res


def generate_servicing(pool: Pool, current):
    res = []
    rental_car = current.get('rental_car')
    in_need_of_service = current.get('in_need_of_service')
    scheduled_service = current.get('scheduled_service')
    res.extend([in_need_of_service, scheduled_service, rental_car])
    res.extend([
        Relation('has', rental_car, scheduled_service),
        Relation('is', rental_car, in_need_of_service),
    ])
    service_reading = pool.get('service_reading', random.randint(0, 5500))
    res.extend([service_reading])
    res.extend([
        Relation('has', rental_car, service_reading),
    ])
    rented_car = current.get('rented_car')
    car_exchange_during_rental = current.get('car_exchange_during_rental')
    rental = current.get('rental')
    open = current.get('open')
    res.extend([rented_car, car_exchange_during_rental, open])
    res.extend([
        Relation('has', rental, rented_car),
        Relation('is', rental, open),
        Relation('incurs', rental, car_exchange_during_rental),
    ])
    return res


def generate_transfer(pool: Pool, current):
    res = []
    car_transfer = current.get('car_transfer')
    transfer_drop_off_date_time = current.get('transfer_drop_off_date_time')
    transferred_car = current.get('transferred_car')
    transfer_drop_off_branch = pool.get('transfer_drop_off_branch', random.randint(0, N_BRANCH))
    local_area = current.get('local_area')
    res.extend([transfer_drop_off_date_time, transferred_car, local_area, car_transfer])
    res.extend([
        Relation('has', car_transfer, transfer_drop_off_date_time),
        Relation('is_owned_by', transferred_car, local_area),
        Relation('has', car_transfer, transferred_car),
        Relation('has', car_transfer, transfer_drop_off_date_time),
        Relation('includes', local_area, transfer_drop_off_branch),
    ])
    country = current.get('country')
    country_of_registration = current.get('country_of_registration')
    international_return = current.get('international_return')
    res.extend([country, country_of_registration, international_return])
    res.extend([
        Relation('has', transfer_drop_off_branch, country),
        Relation('has', international_return, transfer_drop_off_branch),
        Relation('has', international_return, transferred_car),
        Relation('has', transferred_car, country_of_registration),
    ])
    res.extend([
        Relation('has', international_return, transfer_drop_off_branch),
        Relation('is_owned_by', transferred_car, local_area),
        Relation('has', international_return, transferred_car),
        Relation('has', international_return, transfer_drop_off_date_time),
        Relation('includes', local_area, transfer_drop_off_branch),
    ])
    return res


def generate(pool) -> list:
    res = []
    current = Current(pool)
    # TODO rental period that do not overlap for same renter
    res.extend(generate_branch(pool))
    res.extend(generate_rental_rules(pool, current))
    res.extend(generate_payment_rules(pool, current))
    res.extend(generate_diver_rules(pool, current))
    res.extend(generate_return_rules(pool, current))
    res.extend(generate_rental_period(pool, current))
    res.extend(generate_servicing(pool, current))
    res.extend(generate_transfer(pool, current))
    return res


# CONFIG
N_BRANCH = 2

if __name__ == '__main__':
    pool = Pool()
    print(' '.join(map(str, generate(pool))))
