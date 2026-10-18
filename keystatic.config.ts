import { config, fields, collection } from '@keystatic/core';

export default config({
  storage:
    process.env.NODE_ENV === 'production'
      ? {
          kind: 'cloud',
        }
      : {
          kind: 'local',
        },
  cloud: {
    project: 'isd-tech/digital-cards',
  },
  ui: {
    brand: {
      name: 'ISD Tech Digital Cards',
    },
  },
  collections: {
    cards: collection({
      label: 'Team Business Cards',
      slugField: 'slug',
      path: 'content/cards/*',
      format: { data: 'json' },
      schema: {
        slug: fields.slug({
          name: {
            label: 'URL Slug (e.g. nstokes -> cards.isd-tech.com/nstokes)',
            validation: { isRequired: true },
          },
        }),
        firstName: fields.text({
          label: 'First Name',
          validation: { isRequired: true },
        }),
        lastName: fields.text({
          label: 'Last Name',
          validation: { isRequired: true },
        }),
        fullName: fields.text({
          label: 'Full Display Name',
          validation: { isRequired: true },
        }),
        jobTitle: fields.text({
          label: 'Job Title',
          validation: { isRequired: true },
        }),
        company: fields.text({
          label: 'Company Name',
          defaultValue: 'Integrated Security Design Ltd',
          validation: { isRequired: true },
        }),
        mobile: fields.text({
          label: 'Mobile Number (Display)',
          description: 'e.g. +44 7919 897800',
          validation: { isRequired: true },
        }),
        mobileDial: fields.text({
          label: 'Mobile Number (Dialable)',
          description: 'e.g. +447919897800 (no spaces)',
          validation: { isRequired: true },
        }),
        email: fields.text({
          label: 'Email Address',
          validation: { isRequired: true },
        }),
        website: fields.url({
          label: 'Website URL',
          defaultValue: 'https://www.isd-tech.com',
        }),
        websiteLabel: fields.text({
          label: 'Website Display Label',
          defaultValue: 'isd-tech.com',
        }),
        linkedin: fields.url({
          label: 'LinkedIn Profile URL',
        }),
        linkedinLabel: fields.text({
          label: 'LinkedIn Display Label',
        }),
        photoCutout: fields.image({
          label: 'Profile Picture (Cutout PNG or Portrait)',
          directory: 'public/images',
          publicPath: '/images/',
        }),
        address: fields.object(
          {
            building: fields.text({
              label: 'Building / Floor',
              defaultValue: 'Shield House, Ground Floor',
            }),
            street: fields.text({
              label: 'Street Address',
              defaultValue: '294 High Street',
            }),
            city: fields.text({
              label: 'Town / City',
              defaultValue: 'Aldershot',
            }),
            postcode: fields.text({
              label: 'Postcode',
              defaultValue: 'GU12 4LT',
            }),
            country: fields.text({
              label: 'Country',
              defaultValue: 'United Kingdom',
            }),
          },
          {
            label: 'Office Address',
          }
        ),
      },
    }),
  },
});
