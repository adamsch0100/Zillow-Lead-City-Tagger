-- Users table
create table users (
    id bigint primary key generated always as identity,
    email text unique not null,
    password_hash text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Subscriptions table
create table subscriptions (
    id bigint primary key generated always as identity,
    user_id bigint references users(id) not null,
    stripe_subscription_id text unique,
    stripe_customer_id text unique,
    status text not null,
    followupboss_api_key text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Script executions table
create table script_executions (
    id bigint primary key generated always as identity,
    subscription_id bigint references subscriptions(id) not null,
    status text not null,
    leads_processed integer default 0,
    cities_tagged integer default 0,
    error_message text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    completed_at timestamp with time zone
);

-- Add indexes
create index idx_users_email on users(email);
create index idx_subscriptions_user_id on subscriptions(user_id);
create index idx_subscriptions_status on subscriptions(status);
create index idx_script_executions_subscription_id on script_executions(subscription_id);
create index idx_script_executions_created_at on script_executions(created_at);

-- Add updated_at trigger function
create or replace function handle_updated_at()
returns trigger as $$
begin
    new.updated_at = timezone('utc'::text, now());
    return new;
end;
$$ language plpgsql;

-- Add triggers for updated_at
create trigger users_updated_at
    before update on users
    for each row
    execute function handle_updated_at();

create trigger subscriptions_updated_at
    before update on subscriptions
    for each row
    execute function handle_updated_at(); 